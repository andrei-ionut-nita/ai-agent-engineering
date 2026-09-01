"""
Lesson 21: the same ingest/retrieve/generate shape, a chromadb backend.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/03_advanced/21_repointing_retrieval_at_chromadb/lesson.py
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
CHAT_MODEL = "gemini-3.5-flash-lite"

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


def build_collection() -> chromadb.Collection:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)

    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="notes")
    collection.add(
        ids=[path.stem for path in paths],
        documents=texts,
        embeddings=vectors,
        metadatas=[{"source": path.name} for path in paths],
    )
    return collection


def retrieve(query: str, collection: chromadb.Collection, k: int) -> list[str]:
    query_vector = embed_texts([query])[0]
    results = collection.query(query_embeddings=[query_vector], n_results=k)
    documents = results["documents"]
    assert documents is not None
    return documents[0]


def generate_answer(query: str, retrieved_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(retrieved_chunks)
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {query}"""
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def ask(query: str, collection: chromadb.Collection, k: int = 2) -> str:
    # Identical in shape to Lesson 8's ask(): retrieve, then generate.
    # Only what's inside retrieve() changed, from a Python list scan to
    # a chromadb query, everything downstream of it is untouched.
    retrieved = retrieve(query, collection, k)
    return generate_answer(query, retrieved)


def main() -> None:
    collection = build_collection()

    query = "What's the best way to get a crispy pizza crust?"
    answer = ask(query, collection)

    print(f"Q: {query}")
    print(f"A: {answer}")


if __name__ == "__main__":
    main()
