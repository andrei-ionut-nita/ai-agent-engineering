"""
Lesson 4: grading every retrieved chunk, not just the top one.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/01_beginner/04_grading_all_top_k_chunks/lesson.py
"""

import math
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError

load_dotenv()

client = genai.Client()


def call_model(prompt: str) -> str:
    # The free tier's requests-per-minute limit (15/min for this chat
    # model) is easy to hit once a lesson makes several calls back to
    # back. A short backoff-and-retry on a 429 keeps this lesson
    # runnable without asking you to slow down by hand, Lesson 19 puts
    # a number on why this cost adds up.
    for attempt in range(5):
        try:
            response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
            return response.text or ""
        except ClientError as error:
            if error.code == 429 and attempt < 4:
                time.sleep(20)
                continue
            raise
    raise RuntimeError("Exceeded retries calling the model")

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

QUESTION = (
    "Project Aurora's Raspberry Pi writes sensor readings to a SQLite "
    "file on its SD card. Where does that Raspberry Pi physically live "
    "in the house?"
)

# Grading over-fetches: k=3 instead of k=1, so the correct chunk
# (bookshelf.md, ranked 2nd) is even in the pool to be graded at all.
# Grading a chunk that was never retrieved is impossible, over-fetching
# a little before grading is what makes correction-by-filtering
# (Lesson 5) possible in the first place.
K = 3

GRADE_PROMPT = """You are grading whether a retrieved passage is relevant \
enough to help answer a question. Read the question and the passage, \
then respond with exactly one word: "relevant" or "not_relevant".

Question: {question}

Passage:
{passage}"""


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


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def build_vector_store() -> list[dict]:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)
    return [
        {"text": text, "embedding": vector, "source": path.name}
        for path, text, vector in zip(paths, texts, vectors)
    ]


def retrieve(query: str, store: list[dict], k: int) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


def grade_chunk(question: str, chunk_text: str) -> str:
    prompt = GRADE_PROMPT.format(question=question, passage=chunk_text)
    grade = call_model(prompt).strip().lower()
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


def grade_all(question: str, chunks: list[dict]) -> list[dict]:
    return [{**chunk, "grade": grade_chunk(question, chunk["text"])} for chunk in chunks]


def main() -> None:
    store = build_vector_store()
    top_k = retrieve(QUESTION, store, K)

    print(f"Q: {QUESTION}\n")
    print(f"Top-{K} retrieved (before grading):")
    for chunk in top_k:
        print(f"  {chunk['source']} (score={chunk['score']:.4f})")

    graded = grade_all(QUESTION, top_k)
    print(f"\nTop-{K}, graded:")
    for chunk in graded:
        print(f"  {chunk['source']}: {chunk['grade']}")

    relevant_count = sum(1 for chunk in graded if chunk["grade"] == "relevant")
    print(
        f"\n{relevant_count}/{K} chunks graded relevant. Grading every "
        "retrieved chunk, not just the top one, is what makes Lesson 5's "
        "filtering possible: a chunk that scored below the top spot but is "
        "still graded relevant (bookshelf.md, here) can be kept, while the "
        "top-scoring but wrongly-graded chunk (weather-station.md) gets "
        "dropped."
    )


if __name__ == "__main__":
    main()
