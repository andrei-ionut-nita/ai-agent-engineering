"""
Lesson 12: upgrading Lesson 3's binary grade to the paper's real
three-way confidence bucket, correct / ambiguous / incorrect, each
mapped to a distinct action.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/02_intermediate/12_confidence_buckets_and_actions/lesson.py
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
    # grading happens per-strip instead of per-chunk (Lessons 10-12
    # onward routinely make a dozen-plus calls in one run). A short
    # backoff-and-retry on a 429 keeps every lesson runnable without
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

# The paper's real three-way grade, replacing Lesson 3's binary one, now
# that Lessons 10-11 give "ambiguous" something to do (refine and keep,
# but also flag).
GRADE_PROMPT = """You are a strict retrieval evaluator. Grade how \
confident you are that the passage below contains a clear, direct \
answer to the question. Choose exactly one:
- "correct": the passage explicitly states the answer.
- "ambiguous": the passage discusses the same general topic (shares a \
subject, like the same project or the same object) but does NOT \
explicitly state the answer to this specific question.
- "incorrect": the passage is about a different topic altogether and \
has nothing useful to offer this question.
Respond with exactly one word.

Question: {question}

Passage:
{passage}"""

STRIP_GRADE_PROMPT = """You are grading whether a single sentence is \
relevant enough to help answer a question. Respond with exactly one \
word: "relevant" or "not_relevant".

Question: {question}

Sentence:
{sentence}"""


def split_into_strips(text: str) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    strips = []
    for paragraph in paragraphs:
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        strips.extend(s.strip() for s in sentences if s.strip())
    return strips


def grade_confidence(question: str, passage: str) -> str:
    prompt = GRADE_PROMPT.format(question=question, passage=passage)
    grade = call_model(prompt).strip().lower()
    # Check "incorrect" before "correct": the word "correct" is a
    # substring of "incorrect", so checking in the wrong order would
    # misread every "incorrect" response as "correct".
    for bucket in ("incorrect", "ambiguous", "correct"):
        if bucket in grade:
            return bucket
    return "incorrect"


def grade_strip(question: str, strip: str) -> str:
    prompt = STRIP_GRADE_PROMPT.format(question=question, sentence=strip)
    grade = call_model(prompt).strip().lower()
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


def refine(question: str, chunk_text: str) -> str:
    strips = split_into_strips(chunk_text)
    relevant = [s for s in strips if grade_strip(question, s) == "relevant"]
    return " ".join(relevant)


def act_on_grade(question: str, source: str, chunk_text: str, grade: str) -> str:
    if grade == "correct":
        return f"refine and keep -> {refine(question, chunk_text)!r}"
    if grade == "ambiguous":
        refined = refine(question, chunk_text)
        note = refined if refined else "(nothing survived refinement)"
        return f"refine, keep, AND flag for a possible query rewrite -> {note!r}"
    return "discard entirely"


# A constructed passage (not a fixture file verbatim), close in topic
# and vocabulary to weather-station.md's real answer, but deliberately
# stripped of the specific re-oiling schedule, on-topic, not a direct
# answer, exactly the "ambiguous" case Lessons 10-11's refinement gives
# somewhere useful to go.
AMBIGUOUS_PASSAGE = (
    "The most failure-prone part of the whole setup has been the wind "
    "speed sensor, which occasionally needs attention from time to time."
)


def main() -> None:
    correct_source = "weather-station.md"
    incorrect_source = "bookshelf.md"

    candidates = [
        (correct_source, (NOTES_DIR / correct_source).read_text()),
        ("(constructed, ambiguous)", AMBIGUOUS_PASSAGE),
        (incorrect_source, (NOTES_DIR / incorrect_source).read_text()),
    ]

    print(f"Q: {QUESTION}\n")
    for label, chunk_text in candidates:
        grade = grade_confidence(QUESTION, chunk_text)
        action = act_on_grade(QUESTION, label, chunk_text, grade)
        print(f"{label}: {grade}")
        print(f"  action: {action}\n")

    print(
        "Three buckets, three actions: 'correct' chunks are refined and "
        "kept outright (Lesson 11's recomposition). 'incorrect' chunks are "
        "discarded (Lesson 5's filtering). 'ambiguous' chunks, new here, "
        "get refined AND kept, but also raise a flag, this specific "
        "question might benefit from a rewrite (Lessons 6-7) even though "
        "something usable was found, because the grader itself wasn't "
        "confident this was a full answer."
    )


if __name__ == "__main__":
    main()
