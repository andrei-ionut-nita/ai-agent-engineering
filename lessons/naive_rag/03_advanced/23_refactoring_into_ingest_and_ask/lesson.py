"""
Lesson 23: two functions, ingest() and ask(), instead of one long script.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py
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


def ingest(notes_dir: Path, chroma_client) -> chromadb.Collection:
    # Everything Lessons 1-20 called "build the vector store" collapses
    # into this one function: read every document, embed it, add it to
    # a fresh collection. Anything that needs a ready-to-query index
    # calls this once and gets a `Collection` back, no other function
    # in this course needs to know how that index was built.
    paths = sorted(notes_dir.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)

    collection = chroma_client.create_collection(name="notes")
    collection.add(
        ids=[path.stem for path in paths],
        documents=texts,
        embeddings=vectors,
        metadatas=[{"source": path.name} for path in paths],
    )
    return collection


def ask(query: str, collection: chromadb.Collection, k: int = 2) -> str:
    # Everything Lessons 6-15 called "retrieve, then generate" collapses
    # into this one function: given a question and a ready collection,
    # return a grounded answer. Nothing outside this function needs to
    # know retrieval or generation happen at all.
    query_vector = embed_texts([query])[0]
    results = collection.query(query_embeddings=[query_vector], n_results=k)
    documents = results["documents"]
    assert documents is not None
    retrieved_chunks = documents[0]

    if not retrieved_chunks:
        return "I don't have any information relevant to that question."

    context = "\n\n---\n\n".join(retrieved_chunks)
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {query}"""
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def main() -> None:
    notes_dir = Path(__file__).parent.parent.parent / "fixtures" / "notes"
    chroma_client = chromadb.Client()

    collection = ingest(notes_dir, chroma_client)
    print(f"Ingested {collection.count()} documents\n")

    for query in (
        "What's the best way to get a crispy pizza crust?",
        "What is the capital of France?",
    ):
        print(f"Q: {query}")
        print(f"A: {ask(query, collection)}\n")


if __name__ == "__main__":
    main()
