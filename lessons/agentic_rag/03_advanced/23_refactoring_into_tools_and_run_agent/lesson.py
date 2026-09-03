"""
Lesson 23: two functions, ingest() and ask(), the series' shared
Strategy protocol, wrapping tools() and run_agent() internally, and
graduating the hand-rolled list-based store to chromadb.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/03_advanced/23_refactoring_into_tools_and_run_agent/lesson.py
"""

import ast
import operator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"
MAX_STEPS = 4


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
    # Same retrieval idea as every hand-rolled search_notes() since
    # Lesson 4, repointed at chromadb instead of a Python list, the
    # same graduation naive_rag Lesson 21 made, applied here.
    query_vector = embed_texts([query])[0]
    results = collection.query(query_embeddings=[query_vector], n_results=k)
    documents = results["documents"]
    metadatas = results["metadatas"]
    assert documents is not None and metadatas is not None
    return "\n\n---\n\n".join(
        f"[{meta['source']}]\n{doc}" for doc, meta in zip(documents[0], metadatas[0])
    )


def get_current_datetime(timezone: str) -> str:
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M %Z")


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

# The series' shared Strategy protocol's State, for this course:
# a ready-to-query chromadb Collection, plus the tool registry built
# against it. Anything holding a State can call ask() without knowing
# chromadb or this course's toolset are involved at all.
State = tuple[chromadb.Collection, ToolRegistry]


def tools(collection: chromadb.Collection) -> ToolRegistry:
    # Everything Lessons 20-22 called "the registry" collapses into
    # this one function: given a ready collection, build every tool
    # this agent can call, declaration and function bundled together.
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
    # Everything Lessons 10-21 called "the loop" collapses into this
    # one function: given a question and a registry, return a final
    # answer, calling whatever tools the model asks for along the way.
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
    # The Strategy protocol's ingest(docs) -> State, run once, at
    # startup: build the collection, then build the tool registry
    # against it, and hand both back as one State.
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
    registry = tools(collection)
    return collection, registry


def ask(query: str, state: State, k: int = 1) -> str:
    # The Strategy protocol's ask(query, state, k) -> str, run per
    # question. `k` is accepted for protocol compatibility with the
    # rest of this series; this course's tools always retrieve one
    # document per search_notes() call by design (Lesson 10), and
    # handle a question needing more than one document by calling the
    # tool again, not by asking for a bigger k in one call.
    _, registry = state
    return run_agent(query, registry)


def main() -> None:
    notes_dir = Path(__file__).parent.parent.parent / "fixtures" / "notes"
    chroma_client = chromadb.Client()

    collection, registry = ingest(notes_dir, chroma_client)
    print(f"Ingested {collection.count()} documents into chromadb, {len(registry)} tools registered\n")

    state = (collection, registry)
    for query in (
        "How often does the sourdough starter need feeding at room temperature?",
        "What is 15 times 6?",
    ):
        print(f"Q: {query}")
        print(f"A: {ask(query, state)}\n")


if __name__ == "__main__":
    main()
