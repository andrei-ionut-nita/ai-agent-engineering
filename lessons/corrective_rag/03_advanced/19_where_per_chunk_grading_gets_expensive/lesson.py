"""
Lesson 19: timing real grading calls, then projecting what per-chunk
(and per-strip) grading costs as the corpus and k grow.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/03_advanced/19_where_per_chunk_grading_gets_expensive/lesson.py
"""

import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

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


def grade_chunk(question: str, chunk_text: str) -> str:
    grade = call_model(GRADE_PROMPT.format(question=question, passage=chunk_text)).strip().lower()
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


def main() -> None:
    question = "How often does the wind speed sensor need re-oiling?"
    chunk_text = (NOTES_DIR / "weather-station.md").read_text()

    # Measure a handful of real grading calls to get an honest per-call
    # latency, instead of guessing at one.
    n_samples = 3
    start = time.perf_counter()
    for _ in range(n_samples):
        grade_chunk(question, chunk_text)
    elapsed = time.perf_counter() - start
    per_call = elapsed / n_samples

    print(f"Measured {n_samples} real grading calls in {elapsed:.2f}s ({per_call:.2f}s/call average)\n")

    print("Grading calls per question, whole-chunk grading (Lesson 3-9), over-fetched k, sequential:")
    for corpus_size, k in [(5, 3), (100, 10), (10_000, 20)]:
        calls = k
        seconds = calls * per_call
        print(f"  corpus={corpus_size:>6}, k={k:>2}: {calls:>3} grading call(s), ~{seconds:.1f}s if run one at a time")

    print("\nGrading calls per question, STRIP-LEVEL grading (Lesson 10+), ~8 strips/chunk average:")
    strips_per_chunk = 8
    for corpus_size, k in [(5, 3), (100, 10), (10_000, 20)]:
        calls = k * strips_per_chunk
        seconds = calls * per_call
        print(f"  corpus={corpus_size:>6}, k={k:>2}: {calls:>4} grading call(s), ~{seconds:.1f}s if run one at a time")

    print(
        "\nStrip-level grading is strictly more precise (Lesson 10) and "
        f"strictly more expensive, roughly {strips_per_chunk}x the calls of "
        "whole-chunk grading, for the same k. At real scale, sequential, "
        "ungraded-by-nothing calls like this become the dominant cost and "
        "latency of the whole pipeline, worse than embedding or generation. "
        "Lesson 20's pre-filter and Lesson 13's caching are both direct "
        "responses to this exact number."
    )


if __name__ == "__main__":
    main()
