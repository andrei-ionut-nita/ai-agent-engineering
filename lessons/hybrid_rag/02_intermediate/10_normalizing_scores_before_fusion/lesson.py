"""
Lesson 10: min-max vs. z-score normalization, and when a weighted blend
is still worth it instead of RRF. No API calls, sparse scores only.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/02_intermediate/10_normalizing_scores_before_fusion/lesson.py
"""

import math
import re
import statistics
from pathlib import Path

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"
K1 = 1.5
B = 0.75
QUERY = "What is firmware build 20240115 for?"  # one clear winner, a long tail with a nonzero runner-up


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def idf(term: str, documents: list[list[str]]) -> float:
    n = len(documents)
    doc_count = sum(1 for doc in documents if term in doc)
    return math.log((n - doc_count + 0.5) / (doc_count + 0.5) + 1)


def bm25_scores(query: str, names: list[str], token_lists: list[list[str]]) -> dict[str, float]:
    query_tokens = tokenize(query)
    avg_len = sum(len(doc) for doc in token_lists) / len(token_lists)
    scores = {}
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
        scores[name] = score
    return scores


def min_max_normalize(scores: dict[str, float]) -> dict[str, float]:
    values = list(scores.values())
    low, high = min(values), max(values)
    spread = high - low
    if spread == 0:
        return {name: 0.0 for name in scores}
    return {name: (score - low) / spread for name, score in scores.items()}


def z_score_normalize(scores: dict[str, float]) -> dict[str, float]:
    values = list(scores.values())
    mean = statistics.mean(values)
    stdev = statistics.pstdev(values)
    if stdev == 0:
        return {name: 0.0 for name in scores}
    return {name: (score - mean) / stdev for name, score in scores.items()}


def main() -> None:
    paths = sorted(NOTES_DIR.glob("*.md"))
    names = [path.name for path in paths]
    texts = [path.read_text() for path in paths]
    token_lists = [tokenize(text) for text in texts]

    sparse_raw = bm25_scores(QUERY, names, token_lists)
    min_max = min_max_normalize(sparse_raw)
    z_score = z_score_normalize(sparse_raw)

    print(f"Query: {QUERY!r}\n")
    print(f"{'document':22} {'raw BM25':>10} {'min-max':>10} {'z-score':>10}")
    for name in sorted(names, key=lambda n: sparse_raw[n], reverse=True):
        print(f"{name:22} {sparse_raw[name]:10.3f} {min_max[name]:10.3f} {z_score[name]:10.3f}")

    print(
        "\nMost of these documents score at or near zero on this query, one "
        "clear winner and a long flat tail, exactly the skewed shape BM25 "
        "produces on a distinctive token. Min-max stretches that whole tail "
        "out to fill [0, 1] anyway, a non-zero runner-up can look "
        "artificially closer to the winner than it really is. Z-score keeps "
        "the shape of the original distribution (the flat tail stays near "
        "its own mean, clearly separated from the outlier), at the cost of "
        "no longer living on a clean [0, 1] scale, mixing negative and "
        "positive values that need care when combined with a dense score."
    )


if __name__ == "__main__":
    main()
