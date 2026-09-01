"""
Lesson 25: Advanced Capstone - A Complete Naive RAG Service.

No new concepts, this combines Lessons 19-24 into one small web service.
Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/03_advanced/25_advanced_capstone_project/lesson.py

To run this as a real, live server instead:

    uvicorn lesson:app --reload
"""

from contextlib import asynccontextmanager
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"
MIN_SCORE = 0.55
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


def ingest(notes_dir: Path, chroma_client) -> chromadb.Collection:
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
    query_vector = embed_texts([query])[0]
    # chromadb's own distance is smaller-is-more-similar (Lesson 20);
    # converting to a 0-1-style similarity by subtracting from 1 lets
    # this capstone reuse the exact same "similarity >= MIN_SCORE"
    # threshold idea from Lesson 14, on top of a chromadb backend.
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=k,
        include=["documents", "distances", "metadatas"],
    )
    documents = results["documents"]
    distances = results["distances"]
    metadatas = results["metadatas"]
    assert documents is not None and distances is not None and metadatas is not None

    relevant = [
        (doc, meta["source"])
        for doc, distance, meta in zip(documents[0], distances[0], metadatas[0])
        if (1 - distance) >= MIN_SCORE
    ]

    if not relevant:
        return "I don't have any information relevant to that question."

    context = "\n\n".join(f"[Source: {source}]\n{doc}" for doc, source in relevant)
    prompt = f"""Answer the question using only the context below.

Rules:
- If the context doesn't contain the answer, say "I don't have information about that."
- Every claim in your answer must cite which source it came from, like this: (according to garden.md).
- Do not use any knowledge you have that isn't in the context below.

Context:
{context}

Question: {query}"""
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


class AskResponse(BaseModel):
    answer: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    chroma_client = chromadb.Client()
    app.state.collection = ingest(NOTES_DIR, chroma_client)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str, k: int = 2) -> AskResponse:
    return AskResponse(answer=ask(q, app.state.collection, k))


def main() -> None:
    with TestClient(app) as test_client:
        for question in (
            "What's the cold ferment time for the pizza dough?",
            "What is the capital of France?",
        ):
            response = test_client.get("/ask", params={"q": question})
            print(f"GET /ask?q={question!r}")
            print(f"  {response.json()}\n")


if __name__ == "__main__":
    main()
