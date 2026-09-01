"""
Lesson 19: timing both hand-rolled retrievers as the corpus grows.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/03_advanced/19_where_hand_rolled_retrieval_breaks_down/lesson.py
"""

import math
import random
import time

EMBEDDING_DIMENSIONS = 768
VOCAB_SIZE = 500
DOC_LENGTH = 150
K1 = 1.5
B = 0.75


def random_vector() -> list[float]:
    return [random.random() for _ in range(EMBEDDING_DIMENSIONS)]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def dense_linear_scan(query_vector: list[float], vectors: list[list[float]]) -> float:
    start = time.perf_counter()
    scored = [cosine_similarity(query_vector, v) for v in vectors]
    scored.sort(reverse=True)
    return time.perf_counter() - start


def random_document() -> list[str]:
    return [f"word{random.randint(0, VOCAB_SIZE)}" for _ in range(DOC_LENGTH)]


def idf(term: str, documents: list[list[str]]) -> float:
    n = len(documents)
    doc_count = sum(1 for doc in documents if term in doc)
    return math.log((n - doc_count + 0.5) / (doc_count + 0.5) + 1)


def sparse_hand_rolled(query_tokens: list[str], documents: list[list[str]]) -> float:
    start = time.perf_counter()
    avg_len = sum(len(doc) for doc in documents) / len(documents)
    scored = []
    for doc in documents:
        doc_len = len(doc)
        score = 0.0
        for term in query_tokens:
            tf = doc.count(term)
            if tf == 0:
                continue
            # idf() re-scans every document, for every query term, for
            # every document being scored, this is the part that gets
            # expensive fast, it isn't cached or precomputed anywhere.
            numerator = tf * (K1 + 1)
            denominator = tf + K1 * (1 - B + B * doc_len / avg_len)
            score += idf(term, documents) * (numerator / denominator)
        scored.append(score)
    scored.sort(reverse=True)
    return time.perf_counter() - start


def main() -> None:
    query_vector = random_vector()
    query_tokens = [f"word{n}" for n in (1, 50, 100)]

    print(f"{'documents':>10}  {'dense (s)':>10}  {'sparse (s)':>10}")
    for size in (5, 500, 2_000, 5_000):
        dense_vectors = [random_vector() for _ in range(size)]
        dense_elapsed = dense_linear_scan(query_vector, dense_vectors)

        sparse_documents = [random_document() for _ in range(size)]
        sparse_elapsed = sparse_hand_rolled(query_tokens, sparse_documents)

        print(f"{size:>10,}  {dense_elapsed:>10.4f}  {sparse_elapsed:>10.4f}")

    print(
        "\nBoth grow with corpus size, but not at the same rate. Dense "
        "linear scan is one cosine similarity per document, O(n). The "
        "hand-rolled sparse scorer recomputes idf() (itself an O(n) scan) "
        "for every query term, for every document, an O(n * terms) shape "
        "on top of an already-O(n) idf lookup, it gets expensive faster "
        "than dense does as both the corpus and the query grow."
    )


if __name__ == "__main__":
    main()
