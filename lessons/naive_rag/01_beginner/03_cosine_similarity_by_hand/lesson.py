"""
Lesson 3: measuring how similar two embeddings are, with plain math.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/01_beginner/03_cosine_similarity_by_hand/lesson.py
"""

import math

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768


def embed(text: str) -> list[float]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=[text],
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    assert response.embeddings is not None
    values = response.embeddings[0].values
    assert values is not None
    return values


def cosine_similarity(a: list[float], b: list[float]) -> float:
    # The dot product: multiply matching positions together, then sum.
    # Two vectors pointing in a similar direction produce a large dot
    # product; pointing in unrelated directions, a small one.
    dot_product = sum(x * y for x, y in zip(a, b))

    # Each vector's own length (magnitude), by the Pythagorean theorem
    # generalized to 768 dimensions instead of 2.
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))

    # Dividing by both magnitudes removes the effect of vector length,
    # leaving only direction, a number between -1 (opposite meaning) and
    # 1 (identical meaning), with 0 meaning unrelated.
    return dot_product / (magnitude_a * magnitude_b)


def main() -> None:
    query = "How do I keep my tomatoes healthy?"
    related = "The tomato bed is watered daily and grows basil alongside it."
    unrelated = "Practice sessions are thirty minutes a day, five days a week."

    query_vector = embed(query)
    related_vector = embed(related)
    unrelated_vector = embed(unrelated)

    print(f"Query:     {query!r}")
    print(f"Related:   {related!r}")
    print(f"Unrelated: {unrelated!r}\n")

    print(f"Similarity to related text:   {cosine_similarity(query_vector, related_vector):.4f}")
    print(f"Similarity to unrelated text: {cosine_similarity(query_vector, unrelated_vector):.4f}")


if __name__ == "__main__":
    main()
