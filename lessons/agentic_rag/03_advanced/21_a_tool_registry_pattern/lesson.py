"""
Lesson 21: a tool registry, one dict mapping a tool's name to both its
declaration and its real function, replacing if/elif dispatch and
adding a third tool along the way.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/03_advanced/21_a_tool_registry_pattern/lesson.py
"""

import ast
import math
import operator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google import genai
from google.genai import types

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


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def build_vector_store() -> list[dict]:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)
    return [
        {"text": text, "embedding": vector, "source": path.name}
        for path, text, vector in zip(paths, texts, vectors)
    ]


def search_notes(query: str, store: list[dict], k: int = 1) -> str:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    top_k = scored[:k]
    return "\n\n---\n\n".join(f"[{r['source']}]\n{r['text']}" for r in top_k)


def get_current_datetime(timezone: str) -> str:
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M %Z")


_CALC_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


def calculate(expression: str) -> str:
    # Evaluated safely via Python's ast module, no eval()/exec(), and
    # no new dependency: only +, -, *, / over numeric literals are
    # ever executed.
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
    # A single object that carries BOTH halves Lesson 19's bug let
    # drift apart: the declaration the model sees, and the real
    # function that runs when the model asks for it by name.
    declaration: types.FunctionDeclaration
    fn: Callable[..., str]


def build_registry(store: list[dict]) -> dict[str, Tool]:
    # One dict, keyed by tool name. Every entry is guaranteed to have
    # both a declaration and a runnable function, because there is no
    # way to add one without the other, they're the same object.
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
            fn=lambda query: search_notes(query, store),
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
                description="Evaluate a basic arithmetic expression, e.g. '12 * 8' or '240 / 4'.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={"expression": types.Schema(type=types.Type.STRING, description="An arithmetic expression.")},
                    required=["expression"],
                ),
            ),
            fn=calculate,
        ),
    }


def run_agent(query: str, registry: dict[str, Tool], max_steps: int = MAX_STEPS) -> str:
    # run_agent() itself, unchanged in spirit from Lesson 20: it still
    # knows nothing about individual tools. What changed is where its
    # declarations and dispatch both come FROM, the same registry,
    # instead of a hand-maintained Tool(...) list and a separately
    # hand-maintained if/elif chain.
    declarations = [tool.declaration for tool in registry.values()]
    config = types.GenerateContentConfig(tools=[types.Tool(function_declarations=declarations)])
    contents: list[types.Content] = [types.Content(role="user", parts=[types.Part(text=query)])]

    for _ in range(max_steps):
        response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=config)
        calls = response.function_calls
        if not calls:
            return response.text or ""

        call = calls[0]
        result = dispatch(call, registry)

        assert response.candidates is not None
        contents.append(response.candidates[0].content)
        contents.append(
            types.Content(role="user", parts=[types.Part.from_function_response(name=call.name, response=result)])
        )

    return "I wasn't able to fully answer this within the allowed number of search steps."


def dispatch(call: types.FunctionCall, registry: dict[str, Tool]) -> dict[str, str]:
    tool = registry.get(call.name)
    if tool is None:
        # This IS still possible in principle (a stale saved
        # conversation referencing a tool since removed from the
        # registry, for instance), but it can no longer happen just
        # because someone forgot a branch, the registry is the single
        # source of truth for both "is this declared" and "can this be
        # run."
        return {"error": f"Unknown tool: {call.name}"}
    try:
        return {"output": tool.fn(**(call.args or {}))}
    except Exception as error:
        return {"error": f"{type(error).__name__}: {error}"}


def main() -> None:
    store = build_vector_store()
    registry = build_registry(store)

    for question in (
        "What is 240 divided by 4?",
        "How often does the sourdough starter need feeding at room temperature?",
        "What time is it right now in Tokyo?",
    ):
        print(f"Q: {question}")
        print(f"A: {run_agent(question, registry)}\n")

    print(
        f"Registry has {len(registry)} tools: {sorted(registry)}. Adding a fourth\n"
        "would mean adding one more Tool(...) entry to build_registry(), nothing\n"
        "else, Lesson 19's forgotten-branch bug isn't just avoided here, it's not\n"
        "expressible in this structure at all."
    )


if __name__ == "__main__":
    main()
