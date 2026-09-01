"""
Lesson 14: dropping retrieved chunks that aren't actually relevant.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/02_intermediate/14_choosing_k_and_thresholds/lesson.py
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

# Chosen from this course's own Lesson 3 observation: an unrelated
# sentence still scored around 0.50 against a related query, so a
# threshold needs to sit comfortably above that "unrelated baseline,"
# not at some theoretically clean round number.
MIN_SCORE = 0.55


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
    return [{"text": text, "embedding": vector} for text, vector in zip(texts, vectors)]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def retrieve(query: str, store: list[dict], k: int, min_score: float = 0.0) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)

    # The threshold applies after ranking, not instead of it: still find
    # the best matches first, then drop any that don't clear the bar,
    # rather than a fixed count no matter how weak the matches are.
    above_threshold = [record for record in scored if record["score"] >= min_score]
    return above_threshold[:k]


def main() -> None:
    store = build_vector_store()

    relevant_query = "What's the best way to get a crispy pizza crust?"
    unrelated_query = "What is the capital of France?"

    for query in (relevant_query, unrelated_query):
        without_threshold = retrieve(query, store, k=2)
        with_threshold = retrieve(query, store, k=2, min_score=MIN_SCORE)

        print(f"Query: {query!r}")
        print(f"  Without threshold: {len(without_threshold)} chunk(s) returned")
        for r in without_threshold:
            print(f"    score={r['score']:.4f}")
        print(f"  With threshold (min_score={MIN_SCORE}): {len(with_threshold)} chunk(s) returned")
        for r in with_threshold:
            print(f"    score={r['score']:.4f}")
        print()


if __name__ == "__main__":
    main()
