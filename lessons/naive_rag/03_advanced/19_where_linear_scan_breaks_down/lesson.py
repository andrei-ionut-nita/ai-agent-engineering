"""
Lesson 19: timing the list-based vector store as it grows.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/03_advanced/19_where_linear_scan_breaks_down/lesson.py
"""

import math
import random
import time

EMBEDDING_DIMENSIONS = 768


def random_vector() -> list[float]:
    # A random vector stands in for a real embedding here. This lesson
    # is about how search *time* scales with store size, not about
    # meaning, so a real embedding call for every one of potentially
    # 100,000 records would be slow, costly, and beside the point.
    return [random.random() for _ in range(EMBEDDING_DIMENSIONS)]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def linear_scan(query_vector: list[float], vectors: list[list[float]]) -> float:
    start = time.perf_counter()
    scored = [cosine_similarity(query_vector, v) for v in vectors]
    scored.sort(reverse=True)
    return time.perf_counter() - start


def main() -> None:
    query_vector = random_vector()

    for size in (5, 1_000, 10_000, 100_000):
        store_vectors = [random_vector() for _ in range(size)]
        elapsed = linear_scan(query_vector, store_vectors)
        print(f"{size:>7,} records: {elapsed:.4f}s")


if __name__ == "__main__":
    main()
