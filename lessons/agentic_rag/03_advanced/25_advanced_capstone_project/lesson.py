"""
Lesson 25: Advanced Capstone - A Complete Agentic RAG Service.

No new concepts, this combines Lessons 1-24 into one small FastAPI
service. Read README.md in this folder first, then read this file top
to bottom, then run it with:

    uv run python lessons/agentic_rag/03_advanced/25_advanced_capstone_project/lesson.py
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
MAX_STEPS = 5
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

SYSTEM_INSTRUCTION = """You are a personal assistant with access to tools:
search_notes (a personal notes collection covering a sourdough starter, a
home aquarium, a vinyl collection, a guitar pedalboard, and a Japanese
study journal), get_current_datetime, calculate, and grade_passage.

Only call search_notes for questions about the personal topics it
covers, never for general knowledge you can already answer directly.
If a question has more than one distinct part, call search_notes once
per part, with a separate, focused query for each. If you are not
confident a retrieved passage actually answers the question, call
grade_passage to check before relying on it, and try a different query
if it comes back not_relevant.

When you give your final answer, cite the source file (shown in
brackets, like [sourdough-starter.md]) for every fact you took from
search_notes, right after that fact."""


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


GRADE_PROMPT = """You are grading whether a retrieved passage is relevant \
enough to help answer a question. Read the question and the passage, \
then respond with exactly one word: "relevant" or "not_relevant".

Question: {question}

Passage:
{passage}"""


def grade_passage(question: str, passage: str) -> str:
    prompt = GRADE_PROMPT.format(question=question, passage=passage)
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    grade = (response.text or "").strip().lower()
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


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
                description=(
                    "Search a personal notes collection (sourdough starter, "
                    "home aquarium, vinyl collection, guitar pedalboard, and "
                    "a Japanese study journal) for passages relevant to a "
                    "query. Returns passages from ONE source document at a "
                    "time."
                ),
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
        "grade_passage": Tool(
            declaration=types.FunctionDeclaration(
                name="grade_passage",
                description=(
                    "Check whether a passage already retrieved with "
                    "search_notes is actually relevant to a question. "
                    "Returns 'relevant' or 'not_relevant'."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "question": types.Schema(type=types.Type.STRING, description="The original question."),
                        "passage": types.Schema(type=types.Type.STRING, description="The retrieved passage text."),
                    },
                    required=["question", "passage"],
                ),
            ),
            fn=grade_passage,
        ),
    }


def run_agent(query: str, registry: ToolRegistry, max_steps: int = MAX_STEPS) -> str:
    declarations = [tool.declaration for tool in registry.values()]
    config = types.GenerateContentConfig(
        tools=[types.Tool(function_declarations=declarations)], system_instruction=SYSTEM_INSTRUCTION
    )
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
    chroma_client = chromadb.Client()
    app.state.agent_state = ingest(NOTES_DIR, chroma_client)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str) -> AskResponse:
    return AskResponse(answer=ask(q, app.state.agent_state))


def main() -> None:
    with TestClient(app) as test_client:
        questions = [
            "How often does the sourdough starter need feeding at room temperature?",
            "What time is it right now in Lisbon?",
            "What is 8 times 7?",
            "How is the vinyl collection organized, and how far along is the Japanese study journal toward JLPT N3?",
            "What is the chemical symbol for gold?",
        ]
        for question in questions:
            response = test_client.get("/ask", params={"q": question})
            print(f"GET /ask?q={question!r}")
            print(f"  {response.json()}\n")


if __name__ == "__main__":
    main()
