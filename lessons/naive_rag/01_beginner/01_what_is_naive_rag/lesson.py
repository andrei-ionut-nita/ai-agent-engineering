"""
Lesson 1: proving why Naive RAG exists, before building it.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/01_beginner/01_what_is_naive_rag/lesson.py
"""

from dotenv import load_dotenv
from google import genai

load_dotenv()

# The raw Gemini client, no LangChain or LlamaIndex in between. Every
# lesson in this course talks to Gemini through this same object.
client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"

# The real answer lives in this course's own fixture files, something
# Gemini has never seen and cannot know from training alone.
QUESTION = "How often does Project Aurora's wind speed sensor need re-oiling?"


def main() -> None:
    # Ask the question with nothing else, no retrieved context, no
    # document, just the question on its own. This is what every AI
    # product does before RAG is added.
    response = client.models.generate_content(model=CHAT_MODEL, contents=QUESTION)

    print(f"Question: {QUESTION}\n")
    print(f"Gemini, with no context:\n{response.text}\n")
    print(
        "The real answer ('every few months, or readings start drifting low') "
        "lives in a fixture file in this course's fixtures/ folder, something "
        "Gemini has never seen. It either says it doesn't know, or invents a "
        "plausible-sounding number, both of which are exactly the failure "
        "Naive RAG exists to fix.\n"
    )
    print("Naive RAG's four stages, built one at a time starting next lesson:")
    print("  1. Chunk    - split a document into small, retrievable passages")
    print("  2. Embed    - turn each passage (and the question) into a vector")
    print("  3. Retrieve - find the passages whose vectors are closest to the question's")
    print("  4. Generate - hand those passages to Gemini alongside the question")


if __name__ == "__main__":
    main()
