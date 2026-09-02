"""
Lesson 16: failure modes, foregrounding grader/generator circularity -
the grader is the same model family as the generator it's supposed to
be checking, so a confidently-wrong grade can go uncaught the same way
a confidently-wrong retrieval did in naive_rag.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/02_intermediate/16_failure_modes_of_grading_and_rewriting/lesson.py
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

QUESTION = "How often does Project Aurora's wind speed sensor need re-oiling?"

# The REAL answer, from the actual fixture file, for comparison.
REAL_SOURCE = "weather-station.md"

# A deliberately constructed, internally consistent but FALSE passage.
# It directly contradicts weather-station.md's real answer ("every few
# months"). Nothing distinguishes it structurally from a real chunk,
# it's confident, on-topic, and directly addresses the question, it's
# just wrong.
FABRICATED_PASSAGE = (
    "According to Project Aurora's build log, the wind speed sensor's "
    "official manufacturer spec sheet calls for re-oiling every three "
    "days without exception, a maintenance interval the project has "
    "followed closely since the sensor was installed."
)

GRADE_PROMPT = """You are a strict retrieval evaluator. Grade how \
confident you are that the passage below contains a clear, direct \
answer to the question. Choose exactly one: "correct", "ambiguous", or \
"incorrect". Respond with exactly one word.

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


def grade_confidence(question: str, passage: str) -> str:
    prompt = GRADE_PROMPT.format(question=question, passage=passage)
    grade = call_model(prompt).strip().lower()
    for bucket in ("incorrect", "ambiguous", "correct"):
        if bucket in grade:
            return bucket
    return "incorrect"


def generate_answer(question: str, passage: str) -> str:
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{passage}

Question: {question}"""
    return call_model(prompt)


def main() -> None:
    real_passage = (NOTES_DIR / REAL_SOURCE).read_text()

    print(f"Q: {QUESTION}\n")

    print(f"Real passage ({REAL_SOURCE}):")
    real_grade = grade_confidence(QUESTION, real_passage)
    real_answer = generate_answer(QUESTION, real_passage)
    print(f"  Grade: {real_grade}")
    print(f"  Generated answer: {real_answer}\n")

    print("Fabricated passage (constructed for this lesson, contradicts the real one):")
    print(f"  {FABRICATED_PASSAGE!r}\n")
    fake_grade = grade_confidence(QUESTION, FABRICATED_PASSAGE)
    fake_answer = generate_answer(QUESTION, FABRICATED_PASSAGE)
    print(f"  Grade: {fake_grade}")
    print(f"  Generated answer: {fake_answer}\n")

    print(
        "This is grader/generator circularity, demonstrated, not asserted: "
        "the grader rated the fabricated passage 'correct', exactly the "
        "same grade it gave the real one, and generation confidently "
        "repeated the fabricated passage's false claim, in the same "
        "confident tone as the true answer. Nothing in this pipeline ever "
        "checks a passage's claim against reality, grading only asks 'does "
        "this passage directly address the question,' never 'is this "
        "passage's claim actually true.' The grader and the generator are "
        "the same model family, so they share this exact blind spot: "
        "a passage that would fool the generator into a confident wrong "
        "answer also fools the grader into passing that same passage "
        "through. 'Grading fixes retrieval' is an assumption this course "
        "has been making since Lesson 3, this lesson is where it gets "
        "tested, and shown to have a real gap, not just described in "
        "prose."
    )


if __name__ == "__main__":
    main()
