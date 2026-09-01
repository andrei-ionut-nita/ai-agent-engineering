"""
Lesson 6: dense and sparse retrieval, head to head, on the same ten
questions.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/01_beginner/06_dense_vs_sparse_head_to_head/lesson.py
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

# Five bare queries, each just the exact ID/model/product/spec on its
# own, with no surrounding topic words to give dense retrieval anything
# to lean on beyond the token itself. Sparse retrieval's home turf.
LEXICAL_QUESTIONS = [
    ("20240115", "home_network.md"),
    ("E3D-CHT-04", "3d_printer.md"),
    ("Puly Caff Plus", "espresso_machine.md"),
    ("FoliGrow 9-3-6", "houseplants.md"),
    ("8 Nm", "bike_maintenance.md"),
]

# Five paraphrased questions, deliberately avoiding the exact nouns each
# document uses. Dense retrieval's home turf.
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


def dense_top1(query_vector: list[float], names: list[str], vectors: list[list[float]]) -> str:
    scored = [(name, cosine_similarity(query_vector, vector)) for name, vector in zip(names, vectors)]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[0][0]


def idf(term: str, documents: list[list[str]]) -> float:
    n = len(documents)
    doc_count = sum(1 for doc in documents if term in doc)
    return math.log((n - doc_count + 0.5) / (doc_count + 0.5) + 1)


def bm25_top1(query: str, names: list[str], token_lists: list[list[str]]) -> str:
    query_tokens = tokenize(query)
    avg_len = sum(len(doc) for doc in token_lists) / len(token_lists)
    scored = []
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
        scored.append((name, score))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[0][0]


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

    dense_hits, sparse_hits = 0, 0
    dense_hits_by_kind = {"lexical": 0, "semantic": 0}
    sparse_hits_by_kind = {"lexical": 0, "semantic": 0}

    print(f"{'kind':9} {'dense':6} {'sparse':6}  question")
    for (question, expected, kind), query_vector in zip(all_questions, query_vectors):
        dense_pick = dense_top1(query_vector, names, doc_vectors)
        sparse_pick = bm25_top1(question, names, token_lists)
        dense_ok = dense_pick == expected
        sparse_ok = sparse_pick == expected
        dense_hits += dense_ok
        sparse_hits += sparse_ok
        dense_hits_by_kind[kind] += dense_ok
        sparse_hits_by_kind[kind] += sparse_ok
        print(f"{kind:9} {'HIT' if dense_ok else 'MISS':6} {'HIT' if sparse_ok else 'MISS':6}  {question}")

    total = len(all_questions)
    print(f"\nDense overall:  {dense_hits}/{total}   (lexical: {dense_hits_by_kind['lexical']}/5, semantic: {dense_hits_by_kind['semantic']}/5)")
    print(f"Sparse overall: {sparse_hits}/{total}   (lexical: {sparse_hits_by_kind['lexical']}/5, semantic: {sparse_hits_by_kind['semantic']}/5)")


if __name__ == "__main__":
    main()
