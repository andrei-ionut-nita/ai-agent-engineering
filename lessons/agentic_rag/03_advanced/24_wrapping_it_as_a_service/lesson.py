"""
Lesson 24: wrapping ingest() and ask() as a small FastAPI service, the
same recipe naive_rag Lesson 24 used, applied to this course's agent.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/03_advanced/24_wrapping_it_as_a_service/lesson.py

To run this as a real, live server instead:

    uvicorn lesson:app --reload
"""

import ast
import operator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"
MAX_STEPS = 4
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    assert response.embeddings is not None
    result = []
    for embedding in response.embeddings:
        assert embedding.values is not None
        result.append(embedding.values)
    return result


def search_notes(query: str, collection: chromadb.Collection, k: int = 1) -> str:
    query_vector = embed_texts([query])[0]
    results = collection.query(query_embeddings=[query_vector], n_results=k)
    documents = results["documents"]
    metadatas = results["metadatas"]
    assert documents is not None and metadatas is not None
    return "\n\n---\n\n".join(f"[{meta['source']}]\n{doc}" for doc, meta in zip(documents[0], metadatas[0]))


def get_current_datetime(timezone: str) -> str:
    tz = ZoneInfo(timezone)
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M %Z")


_CALC_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


def calculate(expression: str) -> str:
    node = ast.parse(expression, mode="eval").body

    def _eval(n: ast.AST) -> float:
        if isinstance(n, ast.BinOp) and type(n.op) in _CALC_OPS:
            return _CALC_OPS[type(n.op)](_eval(n.left), _eval(n.right))
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        raise ValueError(f"Unsupported expression: {expression!r}")

    return str(_eval(node))


@dataclass
class Tool:
    declaration: types.FunctionDeclaration
    fn: Callable[..., str]


ToolRegistry = dict[str, Tool]
State = tuple[chromadb.Collection, ToolRegistry]


def tools(collection: chromadb.Collection) -> ToolRegistry:
    return {
        "search_notes": Tool(
            declaration=types.FunctionDeclaration(
                name="search_notes",
                description="Search a personal notes collection for passages relevant to a query.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={"query": types.Schema(type=types.Type.STRING, description="What to search for.")},
                    required=["query"],
                ),
            ),
            fn=lambda query: search_notes(query, collection),
        ),
        "get_current_datetime": Tool(
            declaration=types.FunctionDeclaration(
                name="get_current_datetime",
                description="Get the current date and time in a named IANA timezone.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={"timezone": types.Schema(type=types.Type.STRING, description="An IANA timezone name.")},
                    required=["timezone"],
                ),
            ),
            fn=get_current_datetime,
        ),
        "calculate": Tool(
            declaration=types.FunctionDeclaration(
                name="calculate",
                description="Evaluate a basic arithmetic expression.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={"expression": types.Schema(type=types.Type.STRING, description="An arithmetic expression.")},
                    required=["expression"],
                ),
            ),
            fn=calculate,
        ),
    }


def run_agent(query: str, registry: ToolRegistry, max_steps: int = MAX_STEPS) -> str:
    declarations = [tool.declaration for tool in registry.values()]
    config = types.GenerateContentConfig(tools=[types.Tool(function_declarations=declarations)])
    contents: list[types.Content] = [types.Content(role="user", parts=[types.Part(text=query)])]

    for _ in range(max_steps):
        response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=config)
        calls = response.function_calls
        if not calls:
            return response.text or ""

        call = calls[0]
        tool = registry.get(call.name)
        if tool is None:
            result = {"error": f"Unknown tool: {call.name}"}
        else:
            try:
                result = {"output": tool.fn(**(call.args or {}))}
            except Exception as error:
                result = {"error": f"{type(error).__name__}: {error}"}

        assert response.candidates is not None
        contents.append(response.candidates[0].content)
        contents.append(
            types.Content(role="user", parts=[types.Part.from_function_response(name=call.name, response=result)])
        )

    return "I wasn't able to fully answer this within the allowed number of search steps."


def ingest(notes_dir: Path, chroma_client) -> State:
    paths = sorted(notes_dir.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)

    collection = chroma_client.create_collection(name="notes")
    collection.add(
        ids=[path.stem for path in paths],
        documents=texts,
        embeddings=vectors,
        metadatas=[{"source": path.name} for path in paths],
    )
    return collection, tools(collection)


def ask(query: str, state: State, k: int = 1) -> str:
    _, registry = state
    return run_agent(query, registry)


class AskResponse(BaseModel):
    answer: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Exactly naive_rag Lesson 24's shape: ingest() once, at startup,
    # stored on app.state, so every request handler can reach the same
    # already-built State without rebuilding it per request.
    chroma_client = chromadb.Client()
    app.state.agent_state = ingest(NOTES_DIR, chroma_client)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str) -> AskResponse:
    return AskResponse(answer=ask(q, app.state.agent_state))


def main() -> None:
    with TestClient(app) as test_client:
        for question in (
            "How often does the sourdough starter need feeding at room temperature?",
            "What's 9 times 9?",
        ):
            response = test_client.get("/ask", params={"q": question})
            print(f"GET /ask?q={question!r}")
            print(f"  {response.json()}\n")


if __name__ == "__main__":
    main()
