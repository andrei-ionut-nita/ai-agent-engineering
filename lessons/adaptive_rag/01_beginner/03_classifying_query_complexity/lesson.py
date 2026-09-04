"""
Lesson 3: labeling a question's complexity with Gemini, before
retrieving anything.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/01_beginner/03_classifying_query_complexity/lesson.py
"""

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"


class Classification(BaseModel):
    label: str  # one of: simple_factual, multi_hop, ambiguous
    reason: str


CLASSIFY_PROMPT = """Classify the question below into exactly one of
these three labels:

- simple_factual: answerable from a single fact in a single document,
  no combining of separate documents needed.
- multi_hop: the full answer requires combining facts from two or more
  separate documents, no one document has the whole answer.
- ambiguous: the question is genuinely underspecified, or its answer
  reasonably draws on multiple documents from different angles with no
  single document being clearly the right one to check first.

Question: {question}

Give a one-sentence reason for the label you chose."""


def classify(question: str) -> Classification:
    prompt = CLASSIFY_PROMPT.format(question=question)
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Classification,
            temperature=0,
        ),
    )
    assert response.text is not None
    return Classification.model_validate_json(response.text)


def main() -> None:
    questions = [
        # simple_factual: pizza-dough.md alone has this.
        "What oven setting does the pizza dough recipe use?",
        # multi_hop: needs bookshelf.md and cello-practice.md together.
        "What two hobbies happen in the same room as the weather station?",
        # ambiguous: wind speed shows up in weather-station.md (sensor
        # readings) and garden.md (drying out the raised beds), two
        # different angles, no single document is clearly "the" answer.
        "How does wind speed affect things around the house?",
    ]

    for question in questions:
        result = classify(question)
        print(f"Q: {question}")
        print(f"  label:  {result.label}")
        print(f"  reason: {result.reason}\n")


if __name__ == "__main__":
    main()
