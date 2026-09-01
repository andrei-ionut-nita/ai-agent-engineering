"""
Lesson 15: a diagnostic for spotting a query dense retrieval should win,
measuring literal token overlap with the actual answer.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/02_intermediate/15_where_dense_wins/lesson.py
"""

import re
from pathlib import Path

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

# The same ten questions from Lesson 6, with which document actually
# answers each one, known ground truth for this diagnostic.
QUESTIONS = [
    ("20240115", "home_network.md"),
    ("E3D-CHT-04", "3d_printer.md"),
    ("Puly Caff Plus", "espresso_machine.md"),
    ("FoliGrow 9-3-6", "houseplants.md"),
    ("8 Nm", "bike_maintenance.md"),
    ("Why does my video call in the back bedroom keep freezing?", "home_network.md"),
    ("Why do vertical walls have ridges even though I didn't change any settings?", "3d_printer.md"),
    ("Why is my espresso tasting sour and weak lately?", "espresso_machine.md"),
    ("Why does my fig tree keep losing leaves from the bottom?", "houseplants.md"),
    ("Why does my bike skip gears when climbing hills?", "bike_maintenance.md"),
]


# Function words that show up in nearly every document regardless of
# topic. Counting them as "shared vocabulary" would be the same mistake
# Lesson 3's raw term frequency made, common words look like a signal
# when they're really just noise every document has anyway.
STOPWORDS = {
    "a", "an", "and", "are", "at", "but", "by", "does", "doesn", "do",
    "even", "for", "from", "has", "have", "in", "is", "it", "its", "my",
    "of", "on", "or", "so", "t", "that", "the", "though", "to", "was",
    "were", "what", "when", "why", "with", "without",
}


def tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {token for token in tokens if token not in STOPWORDS}


def overlap_ratio(query: str, document_text: str) -> float:
    # What fraction of the query's own *content* tokens (stopwords
    # excluded) appear literally anywhere in the document that actually
    # answers it? A high ratio means sparse retrieval has real tokens to
    # latch onto. A ratio near zero means the query and its answer share
    # almost no meaningful vocabulary at all, exactly the shape only
    # dense retrieval can bridge.
    query_tokens = tokenize(query)
    if not query_tokens:
        return 0.0
    doc_tokens = tokenize(document_text)
    shared = query_tokens & doc_tokens
    return len(shared) / len(query_tokens)


def main() -> None:
    texts_by_name = {path.name: path.read_text() for path in NOTES_DIR.glob("*.md")}

    print(f"{'query':65} {'overlap':8} {'predict':8}")
    for query, expected in QUESTIONS:
        ratio = overlap_ratio(query, texts_by_name[expected])
        prediction = "dense" if ratio < 0.6 else "sparse"
        print(f"{query:65} {ratio:8.2f} {prediction:8}")

    print(
        "\nAll five lexical queries score a perfect 1.00, every content "
        "token they contain appears in the document. The paraphrased "
        "queries land around 0.40-0.50, not zero (a couple of ordinary "
        "setting words like 'back bedroom' do leak through), but well "
        "below the lexical queries, and none of the words doing the real "
        "explanatory work ('firmware', 'nozzle', 'scale', 'nitrogen', "
        "'derailleur') appear in the query at all. That gap, not a literal "
        "zero, is what predicts dense retrieval has to carry these."
    )


if __name__ == "__main__":
    main()
