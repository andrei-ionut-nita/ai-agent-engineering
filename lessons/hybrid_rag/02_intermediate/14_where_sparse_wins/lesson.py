"""
Lesson 14: a diagnostic for spotting a query sparse retrieval should win.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/02_intermediate/14_where_sparse_wins/lesson.py
"""

import re

# A crude but useful rule of thumb: does this token look like an ID
# rather than a word? Digits, hyphens, or an all-caps run longer than a
# typical acronym are all signs an embedding model has little "meaning"
# to place it by, and BM25's literal matching will do better.
ID_SHAPED = re.compile(r"[0-9]|-|^[A-Z]{2,}$")

QUERIES = [
    "20240115",
    "E3D-CHT-04",
    "Puly Caff Plus",
    "8 Nm",
    "FoliGrow 9-3-6",
    "Why does my espresso taste weak and sour lately?",
    "Why does my bike skip gears when climbing hills?",
]


def has_id_shaped_token(query: str) -> bool:
    return any(ID_SHAPED.search(token) for token in query.split())


def main() -> None:
    print(f"{'query':55} {'predict':8}")
    for query in QUERIES:
        prediction = "sparse" if has_id_shaped_token(query) else "dense"
        print(f"{query:55} {prediction:8}")

    print(
        "\nThis is a heuristic, not a guarantee, Lesson 6's actual results "
        "back it up on this course's ten questions, but it can mislead: a "
        "query can contain an ID-shaped token and still need dense "
        "retrieval if the ID itself isn't what distinguishes the right "
        "document (see README)."
    )


if __name__ == "__main__":
    main()
