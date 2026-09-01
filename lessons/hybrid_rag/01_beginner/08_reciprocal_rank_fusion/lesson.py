"""
Lesson 8: Reciprocal Rank Fusion, combining two rankings without scores.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/01_beginner/08_reciprocal_rank_fusion/lesson.py
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
RRF_K = 60  # standard default from the original RRF paper

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

LEXICAL_QUESTIONS = [
    ("20240115", "home_network.md"),
    ("E3D-CHT-04", "3d_printer.md"),
    ("Puly Caff Plus", "espresso_machine.md"),
    ("FoliGrow 9-3-6", "houseplants.md"),
    ("8 Nm", "bike_maintenance.md"),
]

SEMANTIC_QUESTIONS = [
    ("Why does my video call in the back bedroom keep freezing?", "home_network.md"),
    ("Why do vertical walls have ridges even though I didn't change any settings?", "3d_printer.md"),
    ("Why is my espresso tasting sour and weak lately?", "espresso_machine.md"),
    ("Why does my fig tree keep losing leaves from the bottom?", "houseplants.md"),
    ("Why does my bike skip gears when climbing hills?", "bike_maintenance.md"),
]


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
    # For every ranking, a document's contribution is 1 / (k + its rank
    # in that ranking), rank 1 (the best) contributes the most, rank 6
    # (the worst) contributes the least, and there's no score involved
    # at all, just position. Sum each document's contributions across
    # every ranking it appears in, and sort by the total.
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

    all_questions = [(q, a, "lexical") for q, a in LEXICAL_QUESTIONS] + [
        (q, a, "semantic") for q, a in SEMANTIC_QUESTIONS
    ]
    query_vectors = embed_texts([q for q, _, _ in all_questions])

    lexical_hits = semantic_hits = 0
    for (question, expected, kind), query_vector in zip(all_questions, query_vectors):
        dense = dense_ranking(query_vector, names, doc_vectors)
        sparse = sparse_ranking(question, names, token_lists)
        fused = reciprocal_rank_fusion([dense, sparse])
        hit = fused[0] == expected
        if kind == "lexical":
            lexical_hits += hit
        else:
            semantic_hits += hit
        print(f"{kind:9} {'HIT' if hit else 'MISS':5}  {question!r:60}  dense#1={dense[0]:20}  sparse#1={sparse[0]:20}  fused#1={fused[0]}")

    total = lexical_hits + semantic_hits
    print(f"\nRRF (no weight tuned, no scores normalized): {total}/10  (lexical: {lexical_hits}/5, semantic: {semantic_hits}/5)")


if __name__ == "__main__":
    main()
