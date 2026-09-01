"""
Lesson 5: BM25 by hand, TF-IDF's length-normalized, saturating cousin.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/01_beginner/05_bm25_by_hand/lesson.py
"""

import math
import re
from pathlib import Path

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

# Standard defaults from the original Okapi BM25 paper. k1 controls how
# quickly term frequency saturates (lower = saturates faster), b controls
# how strongly document length is penalized (0 = no length normalization
# at all, 1 = fully proportional).
K1 = 1.5
B = 0.75


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def idf(term: str, documents: list[list[str]]) -> float:
    # The "+0.5" smoothing keeps this from going negative for a term
    # that appears in more than half the documents, unlike Lesson 4's
    # plain log(N / df), a detail from the original BM25 paper.
    n = len(documents)
    doc_count = sum(1 for doc in documents if term in doc)
    return math.log((n - doc_count + 0.5) / (doc_count + 0.5) + 1)


def bm25_score(query_tokens: list[str], doc_tokens: list[str], all_docs: list[list[str]], avg_doc_len: float) -> float:
    doc_len = len(doc_tokens)
    score = 0.0
    for term in query_tokens:
        tf = doc_tokens.count(term)
        if tf == 0:
            continue
        term_idf = idf(term, all_docs)
        numerator = tf * (K1 + 1)
        denominator = tf + K1 * (1 - B + B * doc_len / avg_doc_len)
        score += term_idf * (numerator / denominator)
    return score


def search(query: str, documents: dict[str, list[str]]) -> list[tuple[str, float]]:
    query_tokens = tokenize(query)
    all_docs = list(documents.values())
    avg_doc_len = sum(len(doc) for doc in all_docs) / len(all_docs)
    scored = [
        (name, bm25_score(query_tokens, tokens, all_docs, avg_doc_len))
        for name, tokens in documents.items()
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored


def saturation_demo() -> None:
    # A synthetic comparison, independent of the fixture corpus: as one
    # term's raw count in a document climbs, how does its contribution
    # to the score grow? Fixed idf=2.0 and a document sitting exactly at
    # the average length, so only term frequency is varying.
    fixed_idf = 2.0
    avg_len = 140.0
    print("term frequency -> TF-IDF contribution vs. BM25 contribution (same idf, avg-length doc):")
    for tf in (1, 2, 4, 8, 16, 32):
        tfidf_contribution = tf * fixed_idf
        numerator = tf * (K1 + 1)
        denominator = tf + K1 * (1 - B + B * avg_len / avg_len)
        bm25_contribution = fixed_idf * (numerator / denominator)
        print(f"  tf={tf:>2}   TF-IDF={tfidf_contribution:6.2f}   BM25={bm25_contribution:5.2f}")


def main() -> None:
    paths = sorted(NOTES_DIR.glob("*.md"))
    documents = {path.name: tokenize(path.read_text()) for path in paths}

    for query in (
        "Why does it happen and what should I do about it?",
        "What is firmware build 20240115 for?",
    ):
        print(f"Query: {query!r}")
        for name, score in search(query, documents):
            print(f"  {score:6.3f}  {name}")
        print()

    saturation_demo()


if __name__ == "__main__":
    main()
