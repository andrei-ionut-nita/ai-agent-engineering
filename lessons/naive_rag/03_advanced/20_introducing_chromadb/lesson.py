"""
Lesson 20: replacing the hand-rolled list with a real vector database.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/03_advanced/20_introducing_chromadb/lesson.py
"""

from pathlib import Path

import chromadb
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


def main() -> None:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)

    # chromadb.Client() with no arguments is an ephemeral, in-memory
    # database, similar in spirit to this course's own Python list, but
    # with real indexing underneath instead of a linear scan.
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="notes")

    # Unlike this course's own vector store (a list of dicts), chromadb
    # wants each piece kept in its own parallel list: ids, the text
    # itself, the embeddings, and metadata, matched up by position.
    collection.add(
        ids=[path.stem for path in paths],
        documents=texts,
        embeddings=vectors,
        metadatas=[{"source": path.name} for path in paths],
    )

    query = "What's the best way to get a crispy pizza crust?"
    query_vector = embed_texts([query])[0]

    results = collection.query(query_embeddings=[query_vector], n_results=2)

    print(f"Query: {query!r}\n")
    print(f"Collection has {collection.count()} documents\n")
    print("Top 2 results from chromadb:")
    ids = results["ids"][0]
    distances = results["distances"][0]
    for doc_id, distance in zip(ids, distances):
        print(f"  {doc_id}: distance={distance:.4f}")


if __name__ == "__main__":
    main()
