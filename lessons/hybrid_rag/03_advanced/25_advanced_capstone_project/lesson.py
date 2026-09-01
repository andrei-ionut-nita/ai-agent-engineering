"""
Lesson 25: Advanced Capstone - A Complete Hybrid RAG Service.

No new concepts, this combines Lessons 19-24 into one small web service.
Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/03_advanced/25_advanced_capstone_project/lesson.py

To run this as a real, live server instead:

    uvicorn lesson:app --reload
"""

import re
from contextlib import asynccontextmanager
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from google import genai
from google.genai import types
from pydantic import BaseModel
from rank_bm25 import BM25Okapi

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"
RRF_K = 60
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

CATEGORY = {
    "home_network.md": "network",
    "old_travel_router.md": "network",
    "3d_printer.md": "maker",
    "espresso_machine.md": "kitchen",
    "houseplants.md": "garden",
    "bike_maintenance.md": "outdoor",
}


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


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


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = RRF_K) -> list[str]:
    rrf_scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, name in enumerate(ranking, start=1):
            rrf_scores[name] = rrf_scores.get(name, 0.0) + 1 / (k + rank)
    return sorted(rrf_scores, key=lambda name: rrf_scores[name], reverse=True)


class HybridState:
    def __init__(self, collection: chromadb.Collection, bm25: BM25Okapi, names: list[str], texts: list[str]):
        self.collection = collection
        self.bm25 = bm25
        self.names = names
        self.texts = texts


def ingest(notes_dir: Path) -> HybridState:
    paths = sorted(notes_dir.glob("*.md"))
    names = [path.name for path in paths]
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)

    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="notes")
    collection.add(
        ids=names,
        documents=texts,
        embeddings=vectors,
        metadatas=[{"category": CATEGORY[name]} for name in names],
    )

    bm25 = BM25Okapi([tokenize(text) for text in texts])
    return HybridState(collection, bm25, names, texts)


def ask(query: str, state: HybridState, k: int = 2, category: str | None = None) -> str:
    where = {"category": category} if category else None
    query_vector = embed_texts([query])[0]

    dense_results = state.collection.query(
        query_embeddings=[query_vector], n_results=len(state.names), where=where,
    )
    dense_ids = dense_results["ids"]
    assert dense_ids is not None
    dense_ranking = dense_ids[0]

    candidate_names = dense_ranking if category else state.names
    sparse_scores = state.bm25.get_scores(tokenize(query))
    sparse_by_name = dict(zip(state.names, sparse_scores))
    sparse_ranking = sorted(candidate_names, key=lambda n: sparse_by_name[n], reverse=True)

    top_names = reciprocal_rank_fusion([dense_ranking, sparse_ranking])[:k]
    if not top_names:
        return "I don't have any information relevant to that question."

    text_by_name = dict(zip(state.names, state.texts))
    context = "\n\n".join(f"[Source: {name}]\n{text_by_name[name]}" for name in top_names)
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
    app.state.hybrid = ingest(NOTES_DIR)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str, k: int = 2, category: str | None = None) -> AskResponse:
    return AskResponse(answer=ask(q, app.state.hybrid, k, category))


def main() -> None:
    with TestClient(app) as test_client:
        cases = [
            {"q": "20240115"},
            {"q": "Why do vertical walls have ridges even though I didn't change any settings?"},
            {"q": "Which build is the stable one?", "category": "network"},
            {"q": "What is the capital of France?"},
        ]
        for params in cases:
            response = test_client.get("/ask", params=params)
            print(f"GET /ask?{params}")
            print(f"  {response.json()}\n")


if __name__ == "__main__":
    main()
