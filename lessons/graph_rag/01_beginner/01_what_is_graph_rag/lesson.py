"""
Lesson 1: proving why Graph RAG exists, before building it.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/01_beginner/01_what_is_graph_rag/lesson.py
"""

from dotenv import load_dotenv
from google import genai

load_dotenv()

# The raw Gemini client, no LangChain or LlamaIndex in between. Every
# lesson in this course talks to Gemini through this same object.
client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"

# The real answer is split across two of this course's own fixture
# files, something no single retrieved chunk contains on its own.
QUESTION = (
    "Who recalibrated the sensor that Dev flagged as drifting in the "
    "greenhouse, and what tool did they use?"
)


def main() -> None:
    # Ask the question with nothing else: no retrieved context, no
    # document, just the question on its own.
    response = client.models.generate_content(model=CHAT_MODEL, contents=QUESTION)

    print(f"Question: {QUESTION}\n")
    print(f"Gemini, with no context:\n{response.text}\n")
    print(
        "The real answer (Mia recalibrated it, using the multimeter from "
        "the garage electronics bench) is split across two fixture files, "
        "greenhouse.md and maintenance-log.md, neither of which contains "
        "the whole answer on its own. That's a multi-hop question, and "
        "it's what Graph RAG exists to answer.\n"
    )
    print("Graph RAG's shape, built one piece at a time starting next lesson:")
    print("  1. Extract  - pull (subject, relation, object) triples out of each document")
    print("  2. Build    - assemble those triples into a graph of entities and relationships")
    print("  3. Traverse - starting from an entity in the question, hop across relationships")
    print("  4. Generate - hand the facts gathered along the way to Gemini alongside the question")


if __name__ == "__main__":
    main()
