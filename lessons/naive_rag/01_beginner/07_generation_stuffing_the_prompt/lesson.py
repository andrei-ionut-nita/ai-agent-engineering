"""
Lesson 7: handing retrieved chunks to Gemini alongside the question.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/01_beginner/07_generation_stuffing_the_prompt/lesson.py
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
CHAT_MODEL = "gemini-3.5-flash-lite"

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


def load_combined_document() -> str:
    paths = sorted(NOTES_DIR.glob("*.md"))
    blocks = []
    for path in paths:
        _heading, body = path.read_text().split("\n\n", 1)
        blocks.append(" ".join(body.split()))
    return "\n\n".join(blocks)


def chunk_by_paragraph(text: str) -> list[str]:
    raw_chunks = text.split("\n\n")
    return [chunk.strip() for chunk in raw_chunks if chunk.strip()]


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    assert response.embeddings is not None
    result = []
    for embedding in response.embeddings:
        assert embedding.values is not None
        result.append(embedding.values)
    return result


def build_vector_store(chunks: list[str]) -> list[dict]:
    vectors = embed_texts(chunks)
    return [{"text": chunk, "embedding": vector} for chunk, vector in zip(chunks, vectors)]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def retrieve(query: str, store: list[dict], k: int) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


def generate_answer(query: str, retrieved_chunks: list[dict]) -> str:
    # Join every retrieved chunk's text into one block, clearly
    # separated, so Gemini can tell where one ends and the next begins.
    context = "\n\n---\n\n".join(chunk["text"] for chunk in retrieved_chunks)

    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {query}"""

    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def main() -> None:
    text = load_combined_document()
    chunks = chunk_by_paragraph(text)
    store = build_vector_store(chunks)

    query = "What's the best way to get a crispy pizza crust?"
    retrieved = retrieve(query, store, k=2)
    answer = generate_answer(query, retrieved)

    print(f"Question: {query}\n")
    print(f"Answer:\n{answer}")


if __name__ == "__main__":
    main()
