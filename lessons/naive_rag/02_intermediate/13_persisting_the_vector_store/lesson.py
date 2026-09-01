"""
Lesson 13: saving embeddings to disk instead of re-embedding every run.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/02_intermediate/13_persisting_the_vector_store/lesson.py
"""

import json
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"
STORE_PATH = Path(__file__).parent / "store.json"


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


def save_store(store: list[dict], path: Path) -> None:
    # A vector is just a list of floats, and a list of dicts of lists of
    # floats is exactly what JSON is built to represent, no special
    # serialization needed.
    path.write_text(json.dumps(store))


def load_store(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def main() -> None:
    if STORE_PATH.exists():
        start = time.perf_counter()
        store = load_store(STORE_PATH)
        elapsed = time.perf_counter() - start
        print(f"Loaded {len(store)} records from {STORE_PATH.name} in {elapsed:.4f}s")
        print("(no embedding calls made, delete store.json to force re-embedding)")
    else:
        start = time.perf_counter()
        store = build_vector_store()
        elapsed = time.perf_counter() - start
        save_store(store, STORE_PATH)
        print(f"Embedded {len(store)} records and saved to {STORE_PATH.name} in {elapsed:.4f}s")


if __name__ == "__main__":
    main()
