"""
Lesson 18: Intermediate Checkpoint - Notes Search Assistant with Citations.

No new concepts, this combines Lessons 10-17 into one small script.
Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/02_intermediate/18_intermediate_checkpoint_project/lesson.py
"""

import json
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
MIN_SCORE = 0.55

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"
STORE_PATH = Path(__file__).parent / "store.json"


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


def build_vector_store() -> list[dict]:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)
    return [
        {"text": text, "embedding": vector, "source": path.name}
        for path, text, vector in zip(paths, texts, vectors)
    ]


def load_or_build_store() -> list[dict]:
    if STORE_PATH.exists():
        return json.loads(STORE_PATH.read_text())
    store = build_vector_store()
    STORE_PATH.write_text(json.dumps(store))
    return store


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def retrieve(query: str, store: list[dict], k: int, min_score: float = MIN_SCORE) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    above_threshold = [record for record in scored if record["score"] >= min_score]
    return above_threshold[:k]


def generate_answer(query: str, retrieved_chunks: list[dict]) -> str:
    if not retrieved_chunks:
        return "I don't have any information relevant to that question."

    context = "\n\n".join(
        f"[Source: {chunk['source']}]\n{chunk['text']}" for chunk in retrieved_chunks
    )
    prompt = f"""Answer the question using only the context below.

Rules:
- If the context doesn't contain the answer, say "I don't have information about that."
- Every claim in your answer must cite which source it came from, like this: (according to garden.md).
- Do not use any knowledge you have that isn't in the context below.

Context:
{context}

Question: {query}"""
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def ask(query: str, store: list[dict], k: int = 2) -> str:
    retrieved = retrieve(query, store, k)
    return generate_answer(query, retrieved)


def main() -> None:
    store = load_or_build_store()
    print(f"Notes index ready: {len(store)} documents\n")

    questions = [
        "What's the cold ferment time for the pizza dough, and which "
        "numbered raised bed does its basil topping come from?",
        "What is the capital of France?",
    ]

    for question in questions:
        answer = ask(question, store)
        print(f"Q: {question}")
        print(f"A: {answer}\n")


if __name__ == "__main__":
    main()
