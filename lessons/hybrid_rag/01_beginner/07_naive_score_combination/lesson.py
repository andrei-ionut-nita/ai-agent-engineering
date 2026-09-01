"""
Lesson 7: combining dense and sparse scores with a weighted sum, and
watching the right weight change depending on the question.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/01_beginner/07_naive_score_combination/lesson.py
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
    # Dense scores already live in [0, 1] (cosine similarity), but BM25
    # scores are unbounded, could be 0.0, could be 12.4, so they can't be
    # combined directly, whichever one happens to have larger raw numbers
    # would dominate a sum regardless of which is actually more relevant.
    # Min-max squashes both onto the same [0, 1] scale before combining.
    values = list(scores.values())
    low, high = min(values), max(values)
    spread = high - low
    if spread == 0:
        return {name: 0.0 for name in scores}
    return {name: (score - low) / spread for name, score in scores.items()}


def combined_top1(query: str, names: list[str], doc_vectors, query_vector, token_lists, alpha: float) -> str:
    dense_raw = {name: cosine_similarity(query_vector, vector) for name, vector in zip(names, doc_vectors)}
    sparse_raw = bm25_scores(query, names, token_lists)
    dense_norm = min_max_normalize(dense_raw)
    sparse_norm = min_max_normalize(sparse_raw)
    combined = {name: alpha * dense_norm[name] + (1 - alpha) * sparse_norm[name] for name in names}
    return max(combined, key=lambda name: combined[name])


def main() -> None:
    paths = sorted(NOTES_DIR.glob("*.md"))
    names = [path.name for path in paths]
    texts = [path.read_text() for path in paths]
    token_lists = [tokenize(text) for text in texts]
    doc_vectors = embed_texts(texts)

    all_questions = [(q, a, "lexical") for q, a in LEXICAL_QUESTIONS] + [
        (q, a, "semantic") for q, a in SEMANTIC_QUESTIONS
    ]
    query_vectors = embed_texts([q for q, _, _ in all_questions])

    print(f"{'alpha':>7}  {'lexical hits':>13}  {'semantic hits':>14}  {'total':>6}")
    for alpha in (0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0):
        lexical_hits = semantic_hits = 0
        for (question, expected, kind), query_vector in zip(all_questions, query_vectors):
            pick = combined_top1(question, names, doc_vectors, query_vector, token_lists, alpha)
            hit = pick == expected
            if kind == "lexical":
                lexical_hits += hit
            else:
                semantic_hits += hit
        total = lexical_hits + semantic_hits
        print(f"{alpha:7.1f}  {lexical_hits:>13}/5  {semantic_hits:>13}/5  {total:>4}/10")


if __name__ == "__main__":
    main()
