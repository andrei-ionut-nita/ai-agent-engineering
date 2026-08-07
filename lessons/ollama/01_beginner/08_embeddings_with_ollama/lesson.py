"""
Lesson 8: turning text into vectors with a local embedding model.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/01_beginner/08_embeddings_with_ollama/lesson.py

This lesson assumes you've already run, in a terminal:

    ollama pull nomic-embed-text
"""

import math

import ollama

SENTENCES = ["a happy dog", "a joyful puppy", "quarterly tax filing"]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot_product / (norm_a * norm_b)


def main() -> None:
    # nomic-embed-text is a small model trained specifically to produce
    # embeddings, it can't chat or answer questions, embed() is its only
    # job. embed() takes a list of strings and returns one vector per
    # string, in the same order.
    response = ollama.embed(model="nomic-embed-text", input=SENTENCES)

    print(f"Got {len(response.embeddings)} embeddings, each {len(response.embeddings[0])} numbers long.\n")

    dog_vec, puppy_vec, tax_vec = response.embeddings

    # Cosine similarity measures how closely two vectors point in the same
    # direction, 1.0 is identical direction, 0.0 is unrelated. Two
    # sentences about similar ideas should score higher than two about
    # unrelated ones, this is the whole mechanism behind semantic search
    # in the pgvector course, just running locally here.
    print(f"'{SENTENCES[0]}' vs '{SENTENCES[1]}': {cosine_similarity(dog_vec, puppy_vec):.3f}")
    print(f"'{SENTENCES[0]}' vs '{SENTENCES[2]}': {cosine_similarity(dog_vec, tax_vec):.3f}")


if __name__ == "__main__":
    main()
