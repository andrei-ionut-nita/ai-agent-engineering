"""
Lesson 20: replacing the hand-rolled sparse index with rank_bm25.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/03_advanced/20_introducing_rank_bm25/lesson.py
"""

import re
from pathlib import Path

from rank_bm25 import BM25Okapi

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def main() -> None:
    paths = sorted(NOTES_DIR.glob("*.md"))
    names = [path.name for path in paths]
    texts = [path.read_text() for path in paths]
    tokenized_corpus = [tokenize(text) for text in texts]

    # BM25Okapi computes and caches every document's length, the corpus
    # average length, and each term's document frequency once, at
    # construction time, exactly the precomputation this course's
    # hand-rolled idf() never did. Every call to get_scores() afterward
    # reuses that cached work instead of rescanning the corpus.
    bm25 = BM25Okapi(tokenized_corpus)

    for query in ("20240115", "Why is my espresso tasting sour and weak lately?"):
        query_tokens = tokenize(query)
        scores = bm25.get_scores(query_tokens)
        ranked = sorted(zip(names, scores), key=lambda pair: pair[1], reverse=True)
        print(f"Query: {query!r}")
        for name, score in ranked:
            print(f"  {score:6.3f}  {name}")
        print()


if __name__ == "__main__":
    main()
