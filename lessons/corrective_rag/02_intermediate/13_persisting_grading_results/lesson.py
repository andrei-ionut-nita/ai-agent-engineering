"""
Lesson 13: persisting grading results alongside the vector store, so
identical (question, chunk) pairs aren't re-graded every run.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/02_intermediate/13_persisting_grading_results/lesson.py
"""

import hashlib
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"
CACHE_PATH = Path(__file__).parent / "grade_cache.json"

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


def cache_key(question: str, chunk_text: str) -> str:
    # A grade depends on both the question and the exact chunk text, so
    # the cache key hashes both together, if either changes, it's a
    # different grading decision and needs a fresh call.
    digest = hashlib.sha256(f"{question}\n---\n{chunk_text}".encode()).hexdigest()
    return digest


def load_cache() -> dict[str, str]:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text())
    return {}


def save_cache(cache: dict[str, str]) -> None:
    CACHE_PATH.write_text(json.dumps(cache, indent=2))


def grade_chunk_cached(question: str, chunk_text: str, cache: dict[str, str]) -> tuple[str, bool]:
    key = cache_key(question, chunk_text)
    if key in cache:
        return cache[key], True

    prompt = GRADE_PROMPT.format(question=question, passage=chunk_text)
    grade = call_model(prompt).strip().lower()
    grade = "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"
    cache[key] = grade
    return grade, False


def main() -> None:
    question = "How often does the wind speed sensor need re-oiling?"
    chunk_text = (NOTES_DIR / "weather-station.md").read_text()

    cache = load_cache()
    print(f"Cache loaded from {CACHE_PATH.name}: {len(cache)} entr{'y' if len(cache) == 1 else 'ies'}\n")

    for run in (1, 2):
        grade, was_cached = grade_chunk_cached(question, chunk_text, cache)
        source = "cache" if was_cached else "Gemini API call"
        print(f"Run {run}: grade={grade!r}, source={source}")

    save_cache(cache)
    print(
        f"\nSaved {len(cache)} grading result(s) to {CACHE_PATH.name}. Run "
        "this script again and even the first run above will come from "
        "the cache, the exact same (question, chunk) pair was already "
        "graded once."
    )


if __name__ == "__main__":
    main()
