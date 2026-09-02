"""
Lesson 15: prompting for answers that disclose when and why a
correction happened.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/02_intermediate/15_prompting_for_disclosed_corrections/lesson.py
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
enough to help answer a question. Respond with exactly one word: \
"relevant" or "not_relevant".

Question: {question}

Passage:
{passage}"""


def call_model(prompt: str) -> str:
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


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    assert response.embeddings is not None
    return [e.values for e in response.embeddings]  # type: ignore[misc]


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


def generate_disclosed_answer(query: str, graded_chunks: list[dict]) -> str:
    kept = [c for c in graded_chunks if c["grade"] == "relevant"]
    dropped = [c for c in graded_chunks if c["grade"] == "not_relevant"]

    context = "\n\n---\n\n".join(f"[{c['source']}]\n{c['text']}" for c in kept)
    dropped_sources = ", ".join(c["source"] for c in dropped)
    if dropped:
        correction_note = (
            f"Before generating this answer, {len(dropped)} retrieved "
            f"passage(s) that scored high on similarity were graded not "
            f"relevant and dropped, specifically: {dropped_sources}. You "
            "MUST end your answer with one short new sentence starting "
            f"exactly with 'Correction:' explaining that {dropped_sources} "
            "was retrieved but dropped as not relevant to this specific "
            "question."
        )
    else:
        correction_note = "No passages were dropped, nothing to disclose."

    prompt = f"""Answer the question using only the context below, citing \
the source file in brackets like [source.md]. If the context doesn't \
contain the answer, say so, don't guess.

{correction_note}

Context:
{context if context else '(nothing survived grading)'}

Question: {query}"""
    return call_model(prompt)


def main() -> None:
    store = build_vector_store()
    retrieved = retrieve(QUESTION, store, K)
    graded = [{**chunk, "grade": grade_chunk(QUESTION, chunk["text"])} for chunk in retrieved]

    print(f"Q: {QUESTION}\n")
    for chunk in graded:
        print(f"  {chunk['source']}: {chunk['grade']}")

    answer = generate_disclosed_answer(QUESTION, graded)
    print(f"\nA: {answer}")


if __name__ == "__main__":
    main()
