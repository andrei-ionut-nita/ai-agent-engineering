"""
Lesson 2: turning text into a vector with Gemini's embedding model.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/01_beginner/02_your_first_embedding/lesson.py
"""

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

# Used everywhere in this course: short enough to keep vectors small and
# fast to compare by hand, long enough to still capture meaning well.
# This matches this repo's pgvector course, so the two are comparable.
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


def main() -> None:
    text = "The garden's tomato bed is watered every day in summer."
    vector = embed(text)

    print(f"Text: {text!r}\n")
    print(f"Vector length: {len(vector)}")
    print(f"First 5 numbers: {vector[:5]}")
    print(f"Data type of each number: {type(vector[0]).__name__}")


if __name__ == "__main__":
    main()
