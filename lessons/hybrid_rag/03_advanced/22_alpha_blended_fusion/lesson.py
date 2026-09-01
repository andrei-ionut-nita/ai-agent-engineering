"""
Lesson 22: alpha-blended fusion again, this time with real libraries on
both sides, and a fair side-by-side against RRF.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/03_advanced/22_alpha_blended_fusion/lesson.py
"""

import re
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types
from rank_bm25 import BM25Okapi

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
RRF_K = 60
ALPHA = 0.5

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


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


def min_max_normalize(scores: dict[str, float]) -> dict[str, float]:
    values = list(scores.values())
    low, high = min(values), max(values)
    spread = high - low
    if spread == 0:
        return {name: 0.0 for name in scores}
    return {name: (score - low) / spread for name, score in scores.items()}


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = RRF_K) -> list[str]:
    rrf_scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, name in enumerate(ranking, start=1):
            rrf_scores[name] = rrf_scores.get(name, 0.0) + 1 / (k + rank)
    return sorted(rrf_scores, key=lambda name: rrf_scores[name], reverse=True)


def main() -> None:
    paths = sorted(NOTES_DIR.glob("*.md"))
    names = [path.name for path in paths]
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)

    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="notes")
    collection.add(ids=names, documents=texts, embeddings=vectors)

    bm25 = BM25Okapi([tokenize(text) for text in texts])

    for query in ("20240115", "Why do vertical walls have ridges even though I didn't change any settings?"):
        query_vector = embed_texts([query])[0]

        results = collection.query(query_embeddings=[query_vector], n_results=len(names))
        ids = results["ids"][0]
        distances = results["distances"]
        assert distances is not None
        # chromadb returns *distance* (lower is closer), the opposite
        # convention from this course's own cosine similarity, so it's
        # flipped to a similarity-shaped score before anything else.
        dense_scores = {doc_id: 1 - distance for doc_id, distance in zip(ids, distances[0])}
        dense_ranking = ids

        sparse_raw = dict(zip(names, bm25.get_scores(tokenize(query))))
        sparse_ranking = sorted(names, key=lambda n: sparse_raw[n], reverse=True)

        dense_norm = min_max_normalize(dense_scores)
        sparse_norm = min_max_normalize(sparse_raw)
        blended = sorted(
            names,
            key=lambda n: ALPHA * dense_norm[n] + (1 - ALPHA) * sparse_norm[n],
            reverse=True,
        )

        fused = reciprocal_rank_fusion([dense_ranking, sparse_ranking])

        print(f"Query: {query!r}")
        print(f"  alpha-blended (alpha={ALPHA}) top-1: {blended[0]}")
        print(f"  RRF top-1:                       {fused[0]}\n")


if __name__ == "__main__":
    main()
