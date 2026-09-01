"""
Lesson 17: scoring retrieval against a small, hand-labeled answer key.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/02_intermediate/17_minimal_evaluation_precision_at_k/lesson.py
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

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

# The "labeled" part of a labeled evaluation set: for each question,
# which source file a human (you, reading the fixtures) has already
# decided is the correct one to retrieve.
LABELED_QUESTIONS = [
    ("How often does the wind speed sensor need re-oiling?", "weather-station.md"),
    ("What's the cold ferment time for the pizza dough?", "pizza-dough.md"),
    ("How is the bookshelf organized?", "bookshelf.md"),
    ("What piece is being practiced on the cello?", "cello-practice.md"),
    ("Which vegetables grow in the second raised bed?", "garden.md"),
]


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


def retrieve_by_vector(query_vector: list[float], store: list[dict], k: int) -> list[dict]:
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


def precision_at_k(store: list[dict], query_vectors: list[list[float]], k: int) -> float:
    hits = 0
    for (question, expected_source), query_vector in zip(LABELED_QUESTIONS, query_vectors):
        retrieved = retrieve_by_vector(query_vector, store, k)
        retrieved_sources = [r["source"] for r in retrieved]
        hit = expected_source in retrieved_sources
        hits += hit
        print(f"  [{'HIT ' if hit else 'MISS'}] {question!r} -> expected {expected_source}, got {retrieved_sources}")

    return hits / len(LABELED_QUESTIONS)


def main() -> None:
    store = build_vector_store()

    # Every question in the labeled set is embedded once, in a single
    # batch call, and those same vectors are reused for both k=1 and
    # k=2 below, rather than re-embedding the same five questions
    # twice, the same batching lesson from Lesson 5, applied here to
    # stay well under the free tier's requests-per-minute limit.
    questions = [question for question, _ in LABELED_QUESTIONS]
    query_vectors = embed_texts(questions)

    for k in (1, 2):
        print(f"precision@{k}:")
        score = precision_at_k(store, query_vectors, k)
        print(f"  Score: {score:.2f} ({int(score * len(LABELED_QUESTIONS))}/{len(LABELED_QUESTIONS)})\n")


if __name__ == "__main__":
    main()
