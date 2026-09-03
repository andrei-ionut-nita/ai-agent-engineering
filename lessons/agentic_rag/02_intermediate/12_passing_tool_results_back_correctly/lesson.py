"""
Lesson 12: why a tool result has to be attached to the model's own
function-call turn, not just appended as loose text, demonstrated by
deliberately doing it the broken way first.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/02_intermediate/12_passing_tool_results_back_correctly/lesson.py
"""

import math
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"

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


SEARCH_NOTES_DECLARATION = types.FunctionDeclaration(
    name="search_notes",
    description="Search a personal notes collection for passages relevant to a query.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"query": types.Schema(type=types.Type.STRING, description="What to search for.")},
        required=["query"],
    ),
)

TOOLS = types.Tool(function_declarations=[SEARCH_NOTES_DECLARATION])
CONFIG = types.GenerateContentConfig(tools=[TOOLS])

QUESTION = "How often does the vinyl turntable's belt need replacing?"


def broken_ask(query: str, store: list[dict]) -> str:
    # The mistake: skip appending response.candidates[0].content (the
    # model's OWN function_call turn) and just tack the function
    # response straight onto the original contents. This looks
    # reasonable, "here's the question, here's the answer to the call
    # it made", but the API expects every function_response to
    # immediately follow the matching function_call turn that
    # requested it, and this omits that turn entirely.
    contents: list[types.Content] = [types.Content(role="user", parts=[types.Part(text=query)])]
    response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=CONFIG)

    calls = response.function_calls
    assert calls, "expected a tool call for this question"
    call = calls[0]
    result = search_notes(call.args["query"], store)

    # Missing: contents.append(response.candidates[0].content)
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_function_response(name=call.name, response={"result": result})],
        )
    )
    final_response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=CONFIG)
    return final_response.text or ""


def correct_ask(query: str, store: list[dict]) -> str:
    contents: list[types.Content] = [types.Content(role="user", parts=[types.Part(text=query)])]
    response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=CONFIG)

    calls = response.function_calls
    assert calls, "expected a tool call for this question"
    call = calls[0]
    result = search_notes(call.args["query"], store)

    assert response.candidates is not None
    contents.append(response.candidates[0].content)
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_function_response(name=call.name, response={"result": result})],
        )
    )
    final_response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=CONFIG)
    return final_response.text or ""


def main() -> None:
    store = build_vector_store()

    print(f"Q: {QUESTION}\n")

    print("Trying broken_ask() (skips the model's own function_call turn)...")
    try:
        answer = broken_ask(QUESTION, store)
        print(f"  Unexpectedly succeeded: {answer}")
        print(
            "  (Some SDK/model combinations tolerate this omission more than\n"
            "  others; treat a success here as luck, not correctness, see\n"
            "  README for why this shape is still wrong.)"
        )
    except errors.APIError as error:
        print(f"  Failed as expected: {error.code} {error.status} - {error.message}\n")

    print("Trying correct_ask() (replays the model's own turn first)...")
    answer = correct_ask(QUESTION, store)
    print(f"  A: {answer}")


if __name__ == "__main__":
    main()
