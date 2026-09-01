"""
Lesson 21: hybrid retrieval, now with real libraries on both sides,
chromadb for dense, rank_bm25 for sparse, fused with the same RRF from
Lesson 8.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/03_advanced/21_repointing_at_chromadb_and_rank_bm25/lesson.py
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

    # Dense half: same chromadb setup as naive_rag Lesson 20-21, an
    # ephemeral, in-memory collection instead of this course's own list.
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="notes")
    collection.add(ids=names, documents=texts, embeddings=vectors)

    # Sparse half: rank_bm25, Lesson 20, unchanged.
    bm25 = BM25Okapi([tokenize(text) for text in texts])

    for query in ("20240115", "Why do vertical walls have ridges even though I didn't change any settings?"):
        query_vector = embed_texts([query])[0]

        # n_results=len(names) so this returns every document ranked,
        # not just a top-k, RRF needs the full ranking from each side.
        dense_results = collection.query(query_embeddings=[query_vector], n_results=len(names))
        dense_ids = dense_results["ids"]
        assert dense_ids is not None
        dense_ranking = dense_ids[0]

        sparse_scores = bm25.get_scores(tokenize(query))
        sparse_ranking = [name for name, _ in sorted(zip(names, sparse_scores), key=lambda pair: pair[1], reverse=True)]

        fused = reciprocal_rank_fusion([dense_ranking, sparse_ranking])
        print(f"Query: {query!r}")
        print(f"  dense (chromadb):  {dense_ranking}")
        print(f"  sparse (rank_bm25): {sparse_ranking}")
        print(f"  fused (RRF):        {fused}\n")


if __name__ == "__main__":
    main()
