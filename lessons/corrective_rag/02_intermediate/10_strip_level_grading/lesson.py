"""
Lesson 10: grading a chunk's individual sentences (strips), not the
whole chunk at once.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/02_intermediate/10_strip_level_grading/lesson.py
"""

import re
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


def call_model(prompt: str) -> str:
    # The free tier's requests-per-minute limit is easy to hit once
    # grading happens per-strip instead of per-chunk. A short
    # backoff-and-retry on a 429 keeps this lesson runnable without
    # asking you to slow down by hand, Lesson 19 puts a number on why
    # this cost adds up.
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

QUESTION = "How often does the wind speed sensor need re-oiling?"
SOURCE = "weather-station.md"

GRADE_PROMPT = """You are grading whether a single sentence is relevant \
enough to help answer a question. Respond with exactly one word: \
"relevant" or "not_relevant".

Question: {question}

Sentence:
{sentence}"""


def split_into_strips(text: str) -> list[str]:
    # A "strip," in the paper's terms, is a fine-grained piece of a
    # chunk, here, one sentence. Splitting on ". " is crude (it doesn't
    # handle abbreviations), good enough for this course's short, plain
    # fixture notes, and transparent about what it's doing.
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    strips = []
    for paragraph in paragraphs:
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        strips.extend(s.strip() for s in sentences if s.strip())
    return strips


def grade_strip(question: str, strip: str) -> str:
    prompt = GRADE_PROMPT.format(question=question, sentence=strip)
    grade = call_model(prompt).strip().lower()
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


def main() -> None:
    chunk_text = (NOTES_DIR / SOURCE).read_text()
    strips = split_into_strips(chunk_text)

    print(f"Q: {QUESTION}\n")
    print(f"{SOURCE} split into {len(strips)} strips:\n")

    relevant_count = 0
    for i, strip in enumerate(strips, start=1):
        grade = grade_strip(QUESTION, strip)
        relevant_count += grade == "relevant"
        print(f"  [{i}] ({grade}) {strip}")

    print(
        f"\n{relevant_count}/{len(strips)} strips graded relevant. Whole-chunk "
        f"grading (Lesson 3) would have called this entire {len(strips)}-sentence "
        "note either relevant or not, one grade for a chunk that's mostly "
        "about something else, with exactly one sentence that actually "
        "answers this question. Strip-level grading finds that one sentence."
    )


if __name__ == "__main__":
    main()
