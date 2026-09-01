"""
Lesson 6: finding the chunks most relevant to a question.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/01_beginner/06_retrieval_top_k/lesson.py
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


def load_combined_document() -> str:
    paths = sorted(NOTES_DIR.glob("*.md"))
    blocks = []
    for path in paths:
        _heading, body = path.read_text().split("\n\n", 1)
        blocks.append(" ".join(body.split()))
    return "\n\n".join(blocks)


def chunk_by_paragraph(text: str) -> list[str]:
    raw_chunks = text.split("\n\n")
    return [chunk.strip() for chunk in raw_chunks if chunk.strip()]


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


def build_vector_store(chunks: list[str]) -> list[dict]:
    vectors = embed_texts(chunks)
    return [{"text": chunk, "embedding": vector} for chunk, vector in zip(chunks, vectors)]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def retrieve(query: str, store: list[dict], k: int) -> list[dict]:
    query_vector = embed_texts([query])[0]

    # Score every record against the query, highest similarity first.
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)

    return scored[:k]


def main() -> None:
    text = load_combined_document()
    chunks = chunk_by_paragraph(text)
    store = build_vector_store(chunks)

    query = "What's the best way to get a crispy pizza crust?"
    results = retrieve(query, store, k=2)

    print(f"Query: {query!r}\n")
    print(f"Top {len(results)} chunks:\n")
    for i, result in enumerate(results, start=1):
        preview = result["text"][:70]
        print(f"  {i}. (score={result['score']:.4f}) {preview}...")


if __name__ == "__main__":
    main()
