"""
Lesson 16: two failures Naive RAG can't fully fix, seen on purpose.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/02_intermediate/16_failure_modes_by_hand/lesson.py
"""

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
WEATHER_PATH = NOTES_DIR / "weather-station.md"


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


def build_vector_store() -> list[dict]:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)
    return [
        {"text": text, "embedding": vector, "source": path.name}
        for path, text, vector in zip(paths, texts, vectors)
    ]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def retrieve(query: str, store: list[dict], k: int) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


def generate_answer(query: str, retrieved_chunks: list[dict]) -> str:
    context = "\n\n".join(chunk["text"] for chunk in retrieved_chunks)
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain enough information, say so plainly.

Context:
{context}

Question: {query}"""
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def failure_one_multi_hop(store: list[dict]) -> None:
    print("--- Failure 1: a question needing two documents at once ---\n")
    question = (
        "Is the weather station's wind speed reading representative of "
        "conditions in the garden?"
    )

    for k in (1, 2):
        retrieved = retrieve(question, store, k)
        sources = [r["source"] for r in retrieved]
        answer = generate_answer(question, retrieved)
        print(f"k={k}, retrieved: {sources}")
        print(f"Answer: {answer}\n")


def failure_two_split_chunk() -> None:
    print("--- Failure 2: a fact split across a chunk boundary ---\n")
    text = WEATHER_PATH.read_text()

    # Deliberately no overlap, the exact setup Lesson 10 showed splits
    # the word "readings" across two separate chunks.
    size = 110
    chunks = [text[i : i + size] for i in range(0, len(text), size)]

    # Only the single chunk that contains "re-oiling" gets retrieved
    # here, standing in for what a real similarity search would do:
    # rank this chunk highest for a question about sensor maintenance.
    target_chunk = next(c for c in chunks if "re-oiling" in c)
    question = "How often does the sensor need maintenance, and what happens if it's skipped?"

    answer = generate_answer(question, [{"text": target_chunk}])
    print(f"Retrieved chunk: {target_chunk!r}")
    print(f"Answer: {answer}")


def main() -> None:
    store = build_vector_store()
    failure_one_multi_hop(store)
    failure_two_split_chunk()


if __name__ == "__main__":
    main()
