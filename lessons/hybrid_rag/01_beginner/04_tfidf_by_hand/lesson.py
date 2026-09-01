"""
Lesson 4: TF-IDF by hand, downweighting common words, upweighting rare ones.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/01_beginner/04_tfidf_by_hand/lesson.py
"""

import math
import re
from pathlib import Path

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def inverse_document_frequency(term: str, documents: list[list[str]]) -> float:
    # How many of the documents contain this term at least once? A term
    # in every document (like "the" would be, if we hadn't already
    # tokenized it away from punctuation) tells you nothing about which
    # document is relevant. A term in one document out of many is a
    # strong signal. This is that intuition as a number: doc_count in
    # the denominator means "appears everywhere" pushes the score toward
    # zero, "appears almost nowhere" pushes it up.
    doc_count = sum(1 for doc in documents if term in doc)
    if doc_count == 0:
        return 0.0
    return math.log(len(documents) / doc_count)


def tfidf_score(query_tokens: list[str], doc_tokens: list[str], all_docs: list[list[str]]) -> float:
    score = 0.0
    for term in query_tokens:
        term_frequency = doc_tokens.count(term)
        if term_frequency == 0:
            continue
        idf = inverse_document_frequency(term, all_docs)
        score += term_frequency * idf
    return score


def search(query: str, documents: dict[str, list[str]]) -> list[tuple[str, float]]:
    query_tokens = tokenize(query)
    all_docs = list(documents.values())
    scored = [
        (name, tfidf_score(query_tokens, tokens, all_docs))
        for name, tokens in documents.items()
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored


def main() -> None:
    paths = sorted(NOTES_DIR.glob("*.md"))
    documents = {path.name: tokenize(path.read_text()) for path in paths}

    query = "Why does it happen and what should I do about it?"
    print(f"Query: {query!r}")
    print("(Lesson 3's raw term frequency gave: bike_maintenance.md, home_network.md, houseplants.md, 3d_printer.md, espresso_machine.md, barely separated)\n")
    for name, score in search(query, documents):
        print(f"  {score:6.3f}  {name}")

    print(f"\nQuery: 'What is firmware build 20240115 for?'")
    for name, score in search("What is firmware build 20240115 for?", documents):
        print(f"  {score:6.3f}  {name}")


if __name__ == "__main__":
    main()
