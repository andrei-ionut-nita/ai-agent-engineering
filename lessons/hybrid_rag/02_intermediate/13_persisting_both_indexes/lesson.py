"""
Lesson 13: saving both the dense and sparse index to disk, instead of
rebuilding both every run.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/02_intermediate/13_persisting_both_indexes/lesson.py
"""

import json
import re
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


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    assert response.embeddings is not None
    return [embedding.values for embedding in response.embeddings if embedding.values is not None]


def build_store() -> dict:
    paths = sorted(NOTES_DIR.glob("*.md"))
    names = [path.name for path in paths]
    texts = [path.read_text() for path in paths]
    return {
        "names": names,
        # The sparse index needs nothing embedded, tokenized text is
        # already the whole index, just save it as-is.
        "token_lists": [tokenize(text) for text in texts],
        # The dense index is the one expensive part, an embedding API
        # call per document, this is the part persistence actually saves.
        "doc_vectors": embed_texts(texts),
    }


def save_store(store: dict, path: Path) -> None:
    path.write_text(json.dumps(store))


def load_store(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    if STORE_PATH.exists():
        start = time.perf_counter()
        store = load_store(STORE_PATH)
        elapsed = time.perf_counter() - start
        print(f"Loaded {len(store['names'])} documents (dense + sparse) from {STORE_PATH.name} in {elapsed:.4f}s")
        print("(zero embedding calls made, delete store.json to force a rebuild)")
    else:
        start = time.perf_counter()
        store = build_store()
        elapsed = time.perf_counter() - start
        save_store(store, STORE_PATH)
        print(f"Built dense + sparse indexes for {len(store['names'])} documents and saved to {STORE_PATH.name} in {elapsed:.4f}s")


if __name__ == "__main__":
    main()
