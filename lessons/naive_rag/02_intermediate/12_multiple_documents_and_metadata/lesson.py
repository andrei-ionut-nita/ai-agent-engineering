"""
Lesson 12: tagging each chunk with where it came from.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/02_intermediate/12_multiple_documents_and_metadata/lesson.py
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

    # The one new field: which file this chunk came from. Every record
    # so far only had "text" and "embedding"; a real system almost
    # always needs at least this much metadata to be useful.
    return [
        {"text": text, "embedding": vector, "source": path.name}
        for path, text, vector in zip(paths, texts, vectors)
    ]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def retrieve(query: str, store: list[dict], k: int, source: str | None = None) -> list[dict]:
    query_vector = embed_texts([query])[0]

    candidates = store if source is None else [r for r in store if r["source"] == source]

    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in candidates
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


def main() -> None:
    store = build_vector_store()
    print(f"Indexed {len(store)} documents: {[r['source'] for r in store]}\n")

    query = "What maintenance does the sensor need?"

    plain = retrieve(query, store, k=1)
    print(f"Plain search: {plain[0]['source']} (score={plain[0]['score']:.4f})")

    scoped = retrieve(query, store, k=1, source="cello-practice.md")
    print(
        f"Scoped to cello-practice.md only: {scoped[0]['source']} "
        f"(score={scoped[0]['score']:.4f})"
    )


if __name__ == "__main__":
    main()
