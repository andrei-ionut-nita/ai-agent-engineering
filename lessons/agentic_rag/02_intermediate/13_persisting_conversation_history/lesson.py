"""
Lesson 13: saving a multi-turn conversation (questions, tool calls, and
tool results) to disk, and reloading it into a working session instead
of starting over from nothing.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/02_intermediate/13_persisting_conversation_history/lesson.py
"""

import json
import math
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"
HISTORY_PATH = Path(__file__).parent / "conversation_history.json"


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


def ask_turn(contents: list[types.Content], query: str, store: list[dict]) -> str:
    # One turn of a multi-turn session: append the new question to
    # whatever history already exists, then run the same call-tool-call
    # loop from Lesson 10, mutating `contents` in place so the history
    # keeps growing across calls to this function.
    contents.append(types.Content(role="user", parts=[types.Part(text=query)]))

    while True:
        response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=CONFIG)
        calls = response.function_calls
        if not calls:
            assert response.candidates is not None
            contents.append(response.candidates[0].content)
            return response.text or ""

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


def save_history(contents: list[types.Content], path: Path) -> None:
    # Content is a pydantic model (google-genai's types build on
    # pydantic.BaseModel), so model_dump(mode="json") turns the whole
    # structured transcript, roles, text parts, function calls, and
    # function results alike, into plain JSON, the same idea as
    # naive_rag Lesson 13 persisting embeddings, applied to a
    # conversation instead of a vector store.
    raw = [content.model_dump(mode="json") for content in contents]
    path.write_text(json.dumps(raw, indent=2))


def load_history(path: Path) -> list[types.Content]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text())
    return [types.Content.model_validate(item) for item in raw]


def main() -> None:
    store = build_vector_store()

    # Start fresh for this demo run so the output is reproducible.
    if HISTORY_PATH.exists():
        HISTORY_PATH.unlink()

    contents = load_history(HISTORY_PATH)
    print("Turn 1 (fresh session, no history on disk):")
    answer = ask_turn(contents, "How often does the sourdough starter need feeding at room temperature?", store)
    print(f"  A: {answer}")
    save_history(contents, HISTORY_PATH)
    print(f"  Saved {len(contents)} turns to {HISTORY_PATH.name}\n")

    # Simulate a brand new process: forget `contents` entirely and
    # reload it from disk, the way a real session would resume after a
    # restart.
    reloaded_contents = load_history(HISTORY_PATH)
    print(f"Turn 2 (reloaded {len(reloaded_contents)} turns from disk, a new process could do this):")
    answer = ask_turn(reloaded_contents, "What about it makes it smell like acetone?", store)
    print(f"  A: {answer}")
    print(
        "\nThe second question ('it', 'makes it smell') only makes sense\n"
        "because the reloaded history still contains Turn 1's question and\n"
        "answer. Without persisting and reloading `contents`, this follow-up\n"
        "would arrive with no idea what 'it' refers to."
    )


if __name__ == "__main__":
    main()
