"""
Lesson 5: filtering out not-relevant chunks before generation sees them.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/01_beginner/05_filtering_out_incorrect_chunks/lesson.py
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


def filter_relevant(graded_chunks: list[dict]) -> list[dict]:
    # The correction itself: keep only what graded relevant, in whatever
    # order retrieval originally ranked them. A chunk's score no longer
    # matters once it's graded not_relevant, it never reaches generation.
    return [chunk for chunk in graded_chunks if chunk["grade"] == "relevant"]


def generate_answer(query: str, retrieved_chunks: list[dict]) -> str:
    context = "\n\n---\n\n".join(chunk["text"] for chunk in retrieved_chunks)
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {query}"""
    return call_model(prompt)


def main() -> None:
    store = build_vector_store()
    top_k = retrieve(QUESTION, store, K)
    graded = grade_all(QUESTION, top_k)

    print(f"Q: {QUESTION}\n")
    print("Naive answer (top-1, no grading):")
    print(f"  {generate_answer(QUESTION, top_k[:1])}\n")

    filtered = filter_relevant(graded)
    print(f"Graded and filtered: {len(filtered)}/{len(top_k)} chunks kept")
    for chunk in filtered:
        print(f"  kept: {chunk['source']}")
    for chunk in graded:
        if chunk not in filtered:
            print(f"  dropped: {chunk['source']}")

    print(f"\nCorrected answer (graded, filtered):")
    print(f"  {generate_answer(QUESTION, filtered)}")


if __name__ == "__main__":
    main()
