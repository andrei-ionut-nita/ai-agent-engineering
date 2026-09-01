"""
Lesson 16: a query where fusion still fails, because neither retriever
ranked the right document highly to begin with.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/02_intermediate/16_failure_modes_of_hybrid_retrieval/lesson.py
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
RRF_K = 60

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

# This question presupposes its answer looks like "a change that fixed
# something." old_travel_router.md's actual resolution is the opposite,
# deliberately *not* updating the firmware. Neither retriever has any
# mechanism for noticing a query's own premise doesn't match the
# document that answers it, both just look for the closest match.
QUESTION = "What change finally made things work reliably again?"
EXPECTED = "old_travel_router.md"


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
    token_lists = [tokenize(text) for text in texts]
    doc_vectors = embed_texts(texts)
    query_vector = embed_texts([QUESTION])[0]

    dense = dense_ranking(query_vector, names, doc_vectors)
    sparse = sparse_ranking(QUESTION, names, token_lists)
    fused = reciprocal_rank_fusion([dense, sparse])

    print(f"Question: {QUESTION!r}")
    print(f"Correct answer: {EXPECTED}\n")
    print(f"Dense ranking:  {dense}")
    print(f"  {EXPECTED} finished at rank {dense.index(EXPECTED) + 1} of {len(names)}\n")
    print(f"Sparse ranking: {sparse}")
    print(f"  {EXPECTED} finished at rank {sparse.index(EXPECTED) + 1} of {len(names)}\n")
    print(f"Fused ranking:  {fused}")
    print(f"  {EXPECTED} finished at rank {fused.index(EXPECTED) + 1} of {len(names)}")
    print(
        "\nFusion can only recombine what's already in each ranking. If the "
        "right document finished near the bottom in *both*, there's no "
        "position left for it to fuse its way up from."
    )


if __name__ == "__main__":
    main()
