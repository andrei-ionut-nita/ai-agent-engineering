"""
Lesson 5: embedding every chunk once and holding them in a Python list.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/01_beginner/05_an_in_memory_vector_store/lesson.py
"""

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
    # One network call for every chunk at once, instead of one call per
    # chunk, both faster and much friendlier to the free tier's
    # requests-per-minute limit.
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
    # A "vector store," stripped to its essence, is just this: a list of
    # records, each one pairing the original text with its embedding.
    # Everything a real vector database adds on top (persistence,
    # indexing for speed, filtering) is optimization around this same
    # idea, not a different idea.
    return [{"text": chunk, "embedding": vector} for chunk, vector in zip(chunks, vectors)]


def main() -> None:
    text = load_combined_document()
    chunks = chunk_by_paragraph(text)
    store = build_vector_store(chunks)

    print(f"Vector store built: {len(store)} records\n")
    for i, record in enumerate(store, start=1):
        preview = record["text"][:70]
        print(f"  Record {i}: embedding of length {len(record['embedding'])} for: {preview}...")


if __name__ == "__main__":
    main()
