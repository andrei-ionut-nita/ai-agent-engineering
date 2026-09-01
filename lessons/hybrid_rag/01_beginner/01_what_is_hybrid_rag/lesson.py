"""
Lesson 1: watching dense-only retrieval miss an exact detail, on purpose.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/01_beginner/01_what_is_hybrid_rag/lesson.py
"""

import math
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

# A query built entirely around one exact, rare token: a firmware build
# number. The correct document (home_network.md) does contain this exact
# string, but it's surrounded by prose about video calls and brick walls,
# not about firmware at all, so "meaning" alone doesn't obviously point
# here the way it does for a paraphrased question.
QUESTION = "What is firmware build 20240115 for?"


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


def main() -> None:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    doc_vectors = embed_texts(texts)

    query_vector = embed_texts([QUESTION])[0]

    scored = [
        (path.name, cosine_similarity(query_vector, vector))
        for path, vector in zip(paths, doc_vectors)
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)

    print(f"Question: {QUESTION!r}\n")
    print("Dense retrieval ranking (cosine similarity, highest first):")
    for name, score in scored:
        marker = " <- contains the exact string 'firmware build 20240115'" if name == "home_network.md" else ""
        print(f"  {score:.4f}  {name}{marker}")

    top_name, top_score = scored[0]
    print()
    if top_name == "home_network.md":
        runner_up_score = scored[1][1]
        margin = top_score - runner_up_score
        print(
            f"Dense retrieval got the right document this time, but only by "
            f"{margin:.4f}, a thin margin for a question that has exactly one "
            f"correct answer. A single rare token like 'firmware build "
            f"20240115' barely moves an embedding built from the meaning of a "
            f"whole paragraph, this course exists because that margin doesn't "
            f"hold up as documents and questions get less generously written."
        )
    else:
        print(
            f"Dense retrieval's top pick was {top_name!r}, not home_network.md, "
            f"the one document that actually contains 'firmware build "
            f"20240115'. Embeddings capture meaning, not exact tokens, and a "
            f"firmware build number carries almost no meaning on its own, "
            f"this is exactly the gap Hybrid RAG exists to close."
        )


if __name__ == "__main__":
    main()
