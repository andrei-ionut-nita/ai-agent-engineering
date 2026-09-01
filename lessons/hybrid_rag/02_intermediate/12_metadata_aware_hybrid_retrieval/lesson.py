"""
Lesson 12: filtering by metadata, applied identically to both retrievers
before fusing.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/02_intermediate/12_metadata_aware_hybrid_retrieval/lesson.py
"""

import math
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
K1 = 1.5
B = 0.75

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

# Metadata this course's fixtures didn't need until now: one category
# per note, the same idea as naive_rag Lesson 12's "source" filter, just
# a hand-assigned tag instead of the filename itself.
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
    return [embedding.values for embedding in response.embeddings if embedding.values is not None]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def idf(term: str, documents: list[list[str]]) -> float:
    n = len(documents)
    doc_count = sum(1 for doc in documents if term in doc)
    return math.log((n - doc_count + 0.5) / (doc_count + 0.5) + 1)


def dense_ranking(query_vector: list[float], names: list[str], vectors: list[list[float]]) -> list[str]:
    scored = [(name, cosine_similarity(query_vector, vector)) for name, vector in zip(names, vectors)]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [name for name, _ in scored]


def sparse_ranking(query: str, names: list[str], token_lists: list[list[str]]) -> list[str]:
    query_tokens = tokenize(query)
    avg_len = sum(len(doc) for doc in token_lists) / len(token_lists)
    scored = []
    for name, doc_tokens in zip(names, token_lists):
        doc_len = len(doc_tokens)
        score = 0.0
        for term in query_tokens:
            tf = doc_tokens.count(term)
            if tf == 0:
                continue
            numerator = tf * (K1 + 1)
            denominator = tf + K1 * (1 - B + B * doc_len / avg_len)
            score += idf(term, token_lists) * (numerator / denominator)
        scored.append((name, score))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [name for name, _ in scored]


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> list[str]:
    rrf_scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, name in enumerate(ranking, start=1):
            rrf_scores[name] = rrf_scores.get(name, 0.0) + 1 / (k + rank)
    return sorted(rrf_scores, key=lambda name: rrf_scores[name], reverse=True)


def hybrid_search(query: str, all_names: list[str], token_lists: dict, doc_vectors: dict, category: str | None = None) -> list[str]:
    # The filter runs *before* either retriever scores anything, both
    # retrievers only ever see the scoped-down candidate set, so there's
    # no way for an out-of-scope document to sneak into the fused
    # ranking through one retriever and not the other.
    candidates = [n for n in all_names if category is None or CATEGORY[n] == category]
    query_vector = embed_texts([query])[0]
    dense = dense_ranking(query_vector, candidates, [doc_vectors[n] for n in candidates])
    sparse = sparse_ranking(query, candidates, [token_lists[n] for n in candidates])
    return reciprocal_rank_fusion([dense, sparse])


def main() -> None:
    paths = sorted(NOTES_DIR.glob("*.md"))
    names = [path.name for path in paths]
    texts = [path.read_text() for path in paths]
    token_lists = {name: tokenize(text) for name, text in zip(names, texts)}
    doc_vectors = dict(zip(names, embed_texts(texts)))

    query = "Which build is the stable one?"

    plain = hybrid_search(query, names, token_lists, doc_vectors)
    print(f"Query: {query!r}")
    print(f"Plain hybrid search, all {len(names)} documents: {plain}")

    scoped = hybrid_search(query, names, token_lists, doc_vectors, category="network")
    print(f"Scoped to category='network' ({sum(1 for c in CATEGORY.values() if c == 'network')} documents): {scoped}")


if __name__ == "__main__":
    main()
