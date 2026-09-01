"""
Lesson 3: keyword search by hand, raw term-frequency scoring, no API calls.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/01_beginner/03_keyword_search_by_hand/lesson.py
"""

import re
from pathlib import Path

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


def tokenize(text: str) -> list[str]:
    # Lowercase, then split on anything that isn't a letter or digit.
    # "20240115" and "e3d-cht-04" survive as tokens (digits are kept,
    # only the punctuation splits), which is exactly what makes this
    # approach good at exact IDs: no embedding model in the way to blur
    # a rare token into "something about firmware."
    return re.findall(r"[a-z0-9]+", text.lower())


def term_frequency_score(query_tokens: list[str], doc_tokens: list[str]) -> int:
    # The whole algorithm: for every query token, count how many times
    # it appears in this document, and add it up. No weighting, no
    # notion of "rare tokens matter more," just raw counting.
    return sum(doc_tokens.count(token) for token in query_tokens)


def search(query: str, documents: dict[str, list[str]]) -> list[tuple[str, int]]:
    query_tokens = tokenize(query)
    scored = [(name, term_frequency_score(query_tokens, tokens)) for name, tokens in documents.items()]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored


def main() -> None:
    paths = sorted(NOTES_DIR.glob("*.md"))
    documents = {path.name: tokenize(path.read_text()) for path in paths}

    print("Query: 'What is firmware build 20240115 for?'")
    for name, score in search("What is firmware build 20240115 for?", documents):
        print(f"  {score:>2}  {name}")

    print("\nQuery: 'Why does it happen and what should I do about it?'")
    for name, score in search("Why does it happen and what should I do about it?", documents):
        print(f"  {score:>2}  {name}")


if __name__ == "__main__":
    main()
