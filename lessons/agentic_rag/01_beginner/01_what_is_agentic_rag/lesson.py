"""
Lesson 1: proving retrieval isn't always needed, before building a way
for the model to decide for itself.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/01_beginner/01_what_is_agentic_rag/lesson.py
"""

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"

# A question Gemini can answer perfectly well from its own training,
# no document required.
GENERAL_QUESTION = "What temperature does water boil at, at sea level, in Celsius?"

# A question whose real answer lives only in this course's own
# fixtures/notes/sourdough-starter.md, a file Gemini has never seen.
PERSONAL_QUESTION = "How often does Clarence the sourdough starter need feeding at room temperature?"


def main() -> None:
    print(f"Q1 (general knowledge): {GENERAL_QUESTION}")
    response = client.models.generate_content(model=CHAT_MODEL, contents=GENERAL_QUESTION)
    print(f"A1: {response.text}\n")

    print(f"Q2 (needs a private document): {PERSONAL_QUESTION}")
    response = client.models.generate_content(model=CHAT_MODEL, contents=PERSONAL_QUESTION)
    print(f"A2: {response.text}\n")

    print(
        "Q1 came back correct, with nothing retrieved, because Gemini already\n"
        "knew it. Q2 came back either as an admission it doesn't know, or a\n"
        "confident, wrong guess, because the real answer ('every 12 hours')\n"
        "lives only in a fixture file Gemini has never seen.\n"
    )
    print(
        "Every prior course in this series would retrieve for BOTH questions,\n"
        "unconditionally, because their pipelines are wired to always retrieve\n"
        "first and generate second. That wastes an embedding call and a\n"
        "retrieval step on Q1, where it adds nothing.\n"
    )
    print(
        "This course's premise: retrieval should be a tool the model reaches\n"
        "for only when it decides it needs it, the same way it would decide\n"
        "whether to look something up versus just answering, exactly like a\n"
        "person choosing whether to check a notebook before answering a\n"
        "question. Lesson 2 makes the old, fixed-pipeline assumption explicit\n"
        "before Lesson 3 starts loosening it."
    )


if __name__ == "__main__":
    main()
