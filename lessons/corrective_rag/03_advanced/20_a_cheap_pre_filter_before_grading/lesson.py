"""
Lesson 20: a cheap similarity-score pre-filter before the LLM grader
runs at all, to cut grading calls.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/03_advanced/20_a_cheap_pre_filter_before_grading/lesson.py
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

# Chosen the same way naive_rag Lesson 14's threshold was: just above the
# "unrelated sentence" baseline that course's own Lesson 3 observed, not
# from a formula. This is a pre-filter, not a replacement for grading,
# it only needs to be cheap and rule out the obviously-unrelated, the
# LLM grader (Lessons 3, 12) still makes the real call on what's left.
PRE_FILTER_MIN_SCORE = 0.55

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


def retrieve_all_scored(query: str, store: list[dict]) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored


def grade_chunk(question: str, chunk_text: str) -> str:
    grade = call_model(GRADE_PROMPT.format(question=question, passage=chunk_text)).strip().lower()
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


def main() -> None:
    store = build_vector_store()
    question = "Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?"

    all_scored = retrieve_all_scored(question, store)
    print(f"Q: {question}\n")
    print(f"All {len(all_scored)} chunks, scored (no grading yet):")
    for chunk in all_scored:
        print(f"  {chunk['source']}: score={chunk['score']:.4f}")

    without_prefilter = all_scored
    with_prefilter = [c for c in all_scored if c["score"] >= PRE_FILTER_MIN_SCORE]

    print(f"\nWithout pre-filter: {len(without_prefilter)} chunk(s) would need LLM grading")
    print(f"With pre-filter (score >= {PRE_FILTER_MIN_SCORE}): {len(with_prefilter)} chunk(s) need LLM grading")
    print(f"  {[c['source'] for c in with_prefilter]}")

    saved = len(without_prefilter) - len(with_prefilter)
    print(f"\n{saved} grading call(s) skipped entirely, at zero risk to this course's running example:")

    grades = {c["source"]: grade_chunk(question, c["text"]) for c in with_prefilter}
    for source, grade in grades.items():
        print(f"  {source}: {grade}")

    print(
        "\nThe pre-filter is deliberately loose (0.55, not something "
        "tighter), it only needs to rule out chunks that are obviously "
        "unrelated by score alone, cheap, and safe. Anything even "
        "plausibly relevant still goes through the real LLM grader, this "
        "pre-filter cuts cost, it doesn't replace the judgment grading "
        "provides."
    )


if __name__ == "__main__":
    main()
