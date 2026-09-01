"""
Lesson 11: sweeping RRF's k constant, and being honest about how it was
tuned.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/02_intermediate/11_tuning_rrf_k/lesson.py
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

# The exact same ten questions Lesson 6-9 used, and the same ten Lesson
# 17 will report a final score against. Reusing them here to tune `k` is
# the point of this lesson, not an oversight, see README.
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


def reciprocal_rank_fusion(rankings: list[list[str]], k: int) -> list[str]:
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

    all_questions = [(q, a) for q, a in LEXICAL_QUESTIONS + SEMANTIC_QUESTIONS]
    query_vectors = embed_texts([q for q, _ in all_questions])

    rankings_by_question = []
    for (question, expected), query_vector in zip(all_questions, query_vectors):
        dense = dense_ranking(query_vector, names, doc_vectors)
        sparse = sparse_ranking(question, names, token_lists)
        rankings_by_question.append((dense, sparse, expected))

    # k's real effect is on the *full* fused ranking, not just who's on
    # top. This course's six real documents are too easily agreed-upon
    # by dense and sparse to show it (see the sweep below), so this is a
    # synthetic pair of disagreeing rankings, same idea as Lesson 5's
    # synthetic saturation curve.
    synthetic_dense = ["X", "Y", "P", "Q", "R", "S"]
    synthetic_sparse = ["P", "Q", "Y", "R", "S", "X"]
    print("Synthetic example, two rankings that disagree on X and Y:")
    print(f"  dense:  {synthetic_dense}   (X is #1, but dead last in sparse)")
    print(f"  sparse: {synthetic_sparse}   (Y is #3 in both, more consistent)")
    for k in (1, 60, 1000):
        fused = reciprocal_rank_fusion([synthetic_dense, synthetic_sparse], k)
        print(f"  k={k:<5} fused order: {fused}")
    print(
        "\nAt k=1, X's rank-1 finish in dense is worth so much that X "
        "outranks Y despite finishing dead last in sparse. At k=60 (this "
        "course's default from Lesson 8 onward) and beyond, that single "
        "rank-1 finish stops being enough to outweigh X's terrible sparse "
        "rank, and Y, consistently decent in both rankings, overtakes it. "
        "This course's own six real documents don't disagree between "
        "dense and sparse enough for k to move the needle (see the sweep "
        "below), real corpora with more documents and genuine "
        "disagreement between retrievers show this crossover directly.\n"
    )

    print(f"{'k':>6}  {'hits/10':>8}")
    for k in (1, 5, 10, 30, 60, 200, 1000):
        hits = 0
        for dense, sparse, expected in rankings_by_question:
            fused = reciprocal_rank_fusion([dense, sparse], k)
            hits += fused[0] == expected
        print(f"{k:>6}  {hits:>6}/10")

    print(
        "\nEvery one of these ten questions is the exact set Lesson 17 will "
        "report a final precision score against. Sweeping k here and "
        "picking whichever value scores highest, then reporting that same "
        "score in Lesson 17 as evidence hybrid retrieval works, is the "
        "tune/eval contamination naive_rag Lesson 17 warned about, not a "
        "hypothetical, this lesson is doing it, on purpose, so it's visible "
        "rather than hidden. A real pipeline would tune k against one "
        "labeled set and report the score on a separate one."
    )


if __name__ == "__main__":
    main()
