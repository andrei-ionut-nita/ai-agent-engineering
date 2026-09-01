"""
Lesson 9: Beginner Checkpoint - CLI Q&A Assistant.

No new concepts, this combines Lessons 1-8 into one small script.
Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/01_beginner/09_beginner_checkpoint_project/lesson.py
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


def load_documents() -> list[str]:
    # Every fixture file is a short, single-topic note, already about
    # the right size for one chunk, so this folder needs no paragraph
    # splitting the way the single, longer notes.txt file did.
    return [path.read_text() for path in sorted(NOTES_DIR.glob("*.md"))]


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
    context = "\n\n---\n\n".join(chunk["text"] for chunk in retrieved_chunks)
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {query}"""
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def ask(query: str, store: list[dict], k: int = 2) -> str:
    retrieved = retrieve(query, store, k)
    return generate_answer(query, retrieved)


def main() -> None:
    documents = load_documents()
    store = build_vector_store(documents)
    print(f"Loaded and embedded {len(store)} notes from {NOTES_DIR}\n")

    questions = [
        "How often does the wind speed sensor need maintenance?",
        "What's the practice routine for the cello?",
        "Where does the basil topping on the pizza come from?",
    ]

    for question in questions:
        answer = ask(question, store)
        print(f"Q: {question}")
        print(f"A: {answer}\n")


if __name__ == "__main__":
    main()
