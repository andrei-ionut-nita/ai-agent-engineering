"""
Lesson 24: wrapping ingest() and ask() as a small FastAPI service.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/03_advanced/24_wrapping_it_as_a_service/lesson.py

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


class AskResponse(BaseModel):
    answer: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ingestion happens once, when the service starts, not on every
    # request, exactly the same "build once, query many times" shape
    # every lesson since Lesson 5 has used, just moved to run at
    # startup instead of at the top of a script's main().
    chroma_client = chromadb.Client()
    app.state.collection = ingest(NOTES_DIR, chroma_client)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str, k: int = 2) -> AskResponse:
    return AskResponse(answer=ask(q, app.state.collection, k))


def main() -> None:
    # TestClient runs the app in-process, no real network involved,
    # useful for exercising the API the same way `uv run python
    # lesson.py` runs every other lesson, without needing a second
    # terminal running `uvicorn`.
    with TestClient(app) as test_client:
        for question in (
            "What's the best way to get a crispy pizza crust?",
            "What is the capital of France?",
        ):
            response = test_client.get("/ask", params={"q": question})
            print(f"GET /ask?q={question!r}")
            print(f"  {response.json()}\n")


if __name__ == "__main__":
    main()
