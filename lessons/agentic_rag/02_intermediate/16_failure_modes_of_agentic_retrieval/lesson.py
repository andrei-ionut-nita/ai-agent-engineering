"""
Lesson 16: three distinct ways an agentic retrieval loop fails, each
one deliberately triggered, not just described: a malformed/erroring
tool call, unnecessary retrieval, and a loop that never converges.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/02_intermediate/16_failure_modes_of_agentic_retrieval/lesson.py
"""

import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional
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
    # Deliberately NOT try/except here, unlike Lesson 7's version. A
    # bad timezone name raises ZoneInfoNotFoundError, and this lesson
    # wants a real, uncaught exception to reach run_tool_safe(),
    # exactly the shape a tool that "just errors" takes in practice.
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M %Z")


SEARCH_NOTES_DECLARATION = types.FunctionDeclaration(
    name="search_notes",
    description=(
        "Search a personal notes collection (sourdough starter, home "
        "aquarium, vinyl collection, guitar pedalboard, and a Japanese "
        "study journal) for passages relevant to a query."
    ),
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


def run_tool_safe(call: types.FunctionCall, store: list[dict]) -> dict[str, str]:
    # Every tool call goes through here, and every exception, a
    # missing required argument, an invalid one, anything, gets caught
    # and turned into a {"error": ...} dict instead of crashing the
    # whole loop. FunctionResponse.response supports exactly this
    # shape ("output" for success, "error" for failure, per the SDK's
    # own docstring).
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


@dataclass
class FakeCandidate:
    content: types.Content


@dataclass
class FakeResponse:
    function_calls: Optional[list[types.FunctionCall]]
    candidates: list[FakeCandidate]
    text: Optional[str] = None


GenerateFn = Callable[[list[types.Content]], object]


def real_generate_fn(contents: list[types.Content]):
    return client.models.generate_content(model=CHAT_MODEL, contents=contents, config=CONFIG)


def ask(query: str, store: list[dict], generate_fn: GenerateFn = real_generate_fn) -> tuple[str, int, bool]:
    # The Lesson 14 loop, now routing every tool call through
    # run_tool_safe() instead of assuming success, and accepting a
    # swappable generate_fn so this lesson can demonstrate failures
    # deterministically, without depending on the live model happening
    # to misbehave on cue.
    contents: list[types.Content] = [types.Content(role="user", parts=[types.Part(text=query)])]

    for step in range(1, MAX_STEPS + 1):
        response = generate_fn(contents)
        calls = response.function_calls
        if not calls:
            return response.text or "", step - 1, False

        call = calls[0]
        result = run_tool_safe(call, store)

        contents.append(response.candidates[0].content)
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_function_response(name=call.name, response=result)],
            )
        )

    return (
        "I wasn't able to fully answer this within the allowed number of search steps.",
        MAX_STEPS,
        True,
    )


def malformed_call_stub() -> GenerateFn:
    # Deterministically simulates Gemini requesting search_notes with
    # no "query" argument at all, missing required arguments and bad
    # values are the two most common shapes a "malformed tool call"
    # takes in practice. This is deliberately NOT left to chance,
    # relying on the live model to misbehave on cue would make this
    # demonstration unreliable to reproduce.
    calls_made = {"n": 0}

    def stub(contents: list[types.Content]) -> FakeResponse:
        calls_made["n"] += 1
        if calls_made["n"] == 1:
            malformed = types.FunctionCall(name="search_notes", args={})
            content = types.Content(
                role="model", parts=[types.Part.from_function_call(name="search_notes", args={})]
            )
            return FakeResponse(function_calls=[malformed], candidates=[FakeCandidate(content=content)])
        content = types.Content(
            role="model",
            parts=[types.Part(text="I couldn't search the notes, the request was missing required information.")],
        )
        return FakeResponse(
            function_calls=None,
            candidates=[FakeCandidate(content=content)],
            text="I couldn't search the notes, the request was missing required information.",
        )

    return stub


def non_converging_stub() -> GenerateFn:
    # Deterministically simulates a model that ALWAYS asks for another
    # tool call and never concludes it has enough information, exactly
    # the scenario MAX_STEPS exists to survive.
    def stub(contents: list[types.Content]) -> FakeResponse:
        call = types.FunctionCall(name="get_current_datetime", args={"timezone": "UTC"})
        content = types.Content(
            role="model",
            parts=[types.Part.from_function_call(name="get_current_datetime", args={"timezone": "UTC"})],
        )
        return FakeResponse(function_calls=[call], candidates=[FakeCandidate(content=content)])

    return stub


def main() -> None:
    store = build_vector_store()

    print("=== Failure mode 1: a malformed tool call ===")
    answer, steps, hit_limit = ask(
        "What's the feeding schedule for the sourdough starter?", store, generate_fn=malformed_call_stub()
    )
    print(f"  steps: {steps}, hit_limit: {hit_limit}")
    print(f"  A: {answer}")
    print(
        "  The tool call was missing its required 'query' argument. run_tool_safe()\n"
        "  caught the resulting KeyError, turned it into a {'error': ...} function\n"
        "  response, and the loop continued instead of crashing outright.\n"
    )

    print("=== Failure mode 2: unnecessary retrieval ===")
    ambiguous_question = "What's a good daily routine for building a new skill?"
    answer, steps, hit_limit = ask(ambiguous_question, store)
    print(f"  Q: {ambiguous_question}")
    print(f"  steps: {steps}, hit_limit: {hit_limit}")
    print(f"  A: {answer}")
    print(
        "  This question CAN be answered generically, with no personal notes\n"
        "  involved. If steps > 0 above, the model reached for search_notes()\n"
        "  anyway, likely pulled toward language-journal.md by surface-level\n"
        "  topical overlap ('routine', 'skill'), not because retrieval was\n"
        "  actually necessary. This varies by run; treat any nonzero step\n"
        "  count here as evidence, not certainty, unnecessary retrieval is a\n"
        "  tendency this specific tool description doesn't fully prevent, not\n"
        "  a guaranteed outcome every time.\n"
    )

    print("=== Failure mode 3: a non-converging loop ===")
    answer, steps, hit_limit = ask(
        "What time is it?", store, generate_fn=non_converging_stub()
    )
    print(f"  steps: {steps}, hit_limit: {hit_limit}")
    print(f"  A: {answer}")
    print(
        "  This stub always requests another call, never stopping on its own.\n"
        "  MAX_STEPS cut the loop off at 4 iterations and returned an honest\n"
        "  'couldn't finish' message instead of running forever."
    )


if __name__ == "__main__":
    main()
