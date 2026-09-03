"""
Lesson 20: pulling the loop mechanics (call the model, run a tool if
asked, repeat until done or bounded) out into one reusable run_agent()
function, separate from any specific tool's implementation.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/03_advanced/20_structuring_run_agent/lesson.py
"""

import math
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


SEARCH_NOTES_DECLARATION = types.FunctionDeclaration(
    name="search_notes",
    description="Search a personal notes collection for passages relevant to a query.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"query": types.Schema(type=types.Type.STRING, description="What to search for.")},
        required=["query"],
    ),
)

GET_CURRENT_DATETIME_DECLARATION = types.FunctionDeclaration(
    name="get_current_datetime",
    description="Get the current date and time in a named IANA timezone.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"timezone": types.Schema(type=types.Type.STRING, description="An IANA timezone name.")},
        required=["timezone"],
    ),
)

TOOLS = types.Tool(function_declarations=[SEARCH_NOTES_DECLARATION, GET_CURRENT_DATETIME_DECLARATION])
CONFIG = types.GenerateContentConfig(tools=[TOOLS])

DispatchFn = Callable[[types.FunctionCall], dict[str, str]]


def run_agent(query: str, dispatch: DispatchFn, max_steps: int = MAX_STEPS) -> str:
    # Every piece of "how does the loop work" lives here, and nowhere
    # else: build the transcript, call the model, run whatever tool it
    # asked for (by delegating to `dispatch`, not by knowing anything
    # about search_notes or get_current_datetime itself), hand the
    # result back, repeat, bounded. This function has no idea what
    # tools exist; that knowledge lives entirely in `dispatch`,
    # supplied by the caller.
    contents: list[types.Content] = [types.Content(role="user", parts=[types.Part(text=query)])]

    for _ in range(max_steps):
        response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=CONFIG)
        calls = response.function_calls
        if not calls:
            return response.text or ""

        call = calls[0]
        result = dispatch(call)

        assert response.candidates is not None
        contents.append(response.candidates[0].content)
        contents.append(
            types.Content(role="user", parts=[types.Part.from_function_response(name=call.name, response=result)])
        )

    return "I wasn't able to fully answer this within the allowed number of search steps."


def make_dispatch(store: list[dict]) -> DispatchFn:
    # This is the piece Lesson 19's if/elif lived inside of, now
    # isolated into its own small function, built once (closing over
    # `store`) and handed to run_agent() as a plain callable. run_agent()
    # itself never imports search_notes, get_current_datetime, or
    # anything tool-specific.
    def dispatch(call: types.FunctionCall) -> dict[str, str]:
        try:
            args = call.args or {}
            if call.name == "search_notes":
                return {"output": search_notes(args["query"], store)}
            elif call.name == "get_current_datetime":
                return {"output": get_current_datetime(args["timezone"])}
            else:
                return {"error": f"Unknown tool: {call.name}"}
        except Exception as error:
            return {"error": f"{type(error).__name__}: {error}"}

    return dispatch


def main() -> None:
    store = build_vector_store()
    dispatch = make_dispatch(store)

    for question in (
        "How often should the vinyl records get a dust brush before playing?",
        "What time is it right now in Lisbon?",
    ):
        print(f"Q: {question}")
        print(f"A: {run_agent(question, dispatch)}\n")


if __name__ == "__main__":
    main()
