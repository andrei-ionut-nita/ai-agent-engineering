"""
Lesson 20: a cheap rule-based pre-filter in front of the LLM classifier,
to save a Gemini call on questions that are obviously simple.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/03_advanced/20_a_rule_based_pre_filter/lesson.py
"""

import json
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"

MULTI_PART_WORDS = {"and", "both", "also", "compare", "same", "between", "relationship", "affect", "affects"}

# Below this score, a question is confidently simple enough that asking
# Gemini to classify it would be spending a full model call to confirm
# something the cheap signals already agree on. Chosen by inspecting
# Lesson 19's own five example scores (the two clean simple_factual
# questions scored 0.135 and 0.120, everything else scored 0.31+), not
# from this course's Lesson 17 evaluation set, so tuning this number
# doesn't contaminate that later evaluation.
PRE_FILTER_THRESHOLD = 0.20

CLASSIFY_PROMPT = """Classify the question below as exactly one of:
simple_factual, multi_hop, ambiguous.

simple_factual: answerable from a single fact in a single document.
multi_hop: requires combining facts from two or more documents.
ambiguous: the question's scope or intent isn't fully clear, or it
touches more than one topic without a clean single answer.

Return ONLY a JSON object like {{"label": "simple_factual"}}.

Question: {question}"""


def word_count(query: str) -> int:
    return len(query.split())


def keyword_density(query: str) -> float:
    words = re.findall(r"[a-z0-9']+", query.lower())
    if not words:
        return 0.0
    hits = sum(1 for word in words if word in MULTI_PART_WORDS)
    return hits / len(words)


def entity_count(query: str) -> int:
    words = query.split()
    count = 0
    for index, word in enumerate(words):
        stripped = word.strip("?,.")
        if stripped and stripped[0].isupper() and index != 0:
            count += 1
    return count


def complexity_score(query: str) -> float:
    length_signal = min(word_count(query) / 20, 1.0)
    density_signal = min(keyword_density(query) * 4, 1.0)
    entity_signal = min(entity_count(query) / 3, 1.0)
    return round(0.3 * length_signal + 0.4 * density_signal + 0.3 * entity_signal, 3)


def classify_with_llm(query: str) -> str:
    prompt = CLASSIFY_PROMPT.format(question=query)
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0),
    )
    assert response.text is not None
    return json.loads(response.text)["label"]


def classify(query: str) -> tuple[str, bool]:
    # Returns (label, called_llm). The pre-filter only ever produces
    # "simple_factual", confidently, never the other two labels, those
    # still need the real classifier because the cheap signals in
    # Lesson 19 aren't precise enough to tell "multi_hop" apart from
    # "ambiguous" on their own, only "clearly simple" from "not."
    score = complexity_score(query)
    if score < PRE_FILTER_THRESHOLD:
        return "simple_factual", False
    return classify_with_llm(query), True


QUESTIONS = [
    "What oven setting does the pizza dough recipe use?",
    "How often does the wind sensor need re-oiling?",
    "What two hobbies happen in the same room as the weather station?",
    "How does wind speed affect things around the house?",
]


def main() -> None:
    llm_calls = 0
    for query in QUESTIONS:
        label, called_llm = classify(query)
        llm_calls += called_llm
        source = "LLM classifier" if called_llm else "rule-based pre-filter"
        print(f"Q: {query}")
        print(f"   label={label}  (via {source})\n")

    print(f"Gemini classification calls made: {llm_calls} / {len(QUESTIONS)} questions")


if __name__ == "__main__":
    main()
