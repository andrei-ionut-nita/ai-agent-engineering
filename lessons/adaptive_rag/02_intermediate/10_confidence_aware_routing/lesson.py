"""
Lesson 10: extending the classifier to also return a confidence score,
so a router can eventually tell "sure" apart from "guessing" (Lesson 11
does something with that difference).

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/02_intermediate/10_confidence_aware_routing/lesson.py
"""

import json
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

LABELS = ["simple_factual", "multi_hop", "ambiguous"]

# Beginner Lessons 3-6 built a classifier that returns only a label. This
# lesson asks the model for one more field in the same call: how sure it
# is about that label, a number from 0 to 1. Nothing about the question
# the model is answering changes, only what it's allowed to say about its
# own answer.
CLASSIFY_PROMPT = """You are routing questions to a retrieval strategy \
over a small personal notes collection (documents about a weather \
station, a garden, a pizza dough recipe, a bookshelf, and cello \
practice).

Classify the question below into exactly one label:
- "simple_factual": a specific factual lookup that a single passage in \
ONE document would directly answer (a number, a setting, a schedule). \
This is the default for any concrete, well-scoped question.
- "multi_hop": answering it explicitly requires combining facts that \
live in TWO DIFFERENT documents.
- "ambiguous": the question itself is vague, underspecified, or its \
scope could plausibly span more than one unrelated document without \
the question saying so.

Most well-formed, specific questions are "simple_factual". Only use
"multi_hop" or "ambiguous" when the question clearly demands it.

Also rate your confidence in that label from 0.0 (a coin flip) to 1.0
(certain).

Question: {question}"""

CLASSIFY_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "label": types.Schema(type=types.Type.STRING, enum=LABELS),
        "confidence": types.Schema(type=types.Type.NUMBER),
    },
    required=["label", "confidence"],
)


def classify_with_confidence(question: str) -> tuple[str, float]:
    prompt = CLASSIFY_PROMPT.format(question=question)
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CLASSIFY_SCHEMA,
            temperature=0,
        ),
    )
    assert response.text is not None
    result = json.loads(response.text)
    return result["label"], float(result["confidence"])


def main() -> None:
    # A clean single-document lookup: nothing about it points to more
    # than one file, so the label should come back with high confidence.
    clear_question = "What oven setting does the pizza dough recipe use?"

    # This one genuinely straddles two documents (wind speed shows up in
    # both weather-station.md's sensor readings and garden.md's note
    # about drying out the raised beds), with no single-document phrasing
    # that settles it. A good classifier should be less sure here, not
    # just differently sure.
    ambiguous_question = "How does wind speed affect things around the house?"

    for question in (clear_question, ambiguous_question):
        label, confidence = classify_with_confidence(question)
        print(f"Q: {question}")
        print(f"  label: {label}")
        print(f"  confidence: {confidence:.2f}\n")

    print(
        "The label alone can't tell these two questions apart in kind, "
        "both come back with some label. The confidence score is what "
        "separates 'this question clearly belongs on one route' from "
        "'the classifier is guessing here,' and Lesson 11 is what "
        "actually does something with that difference."
    )


if __name__ == "__main__":
    main()
