"""
Lesson 1: what Corrective RAG fixes, before building it.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/01_beginner/01_what_is_corrective_rag/lesson.py
"""

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"

# A question naive top-1 retrieval answers with a wrong-but-confident
# chunk: the correct answer lives in a different fixture file than the
# one that scores highest. Lesson 2 reproduces this with real
# embeddings; this lesson just states the shape of the problem.
QUESTION = (
    "Project Aurora's Raspberry Pi writes sensor readings to a SQLite "
    "file on its SD card. Where does that Raspberry Pi physically live "
    "in the house?"
)


def main() -> None:
    response = client.models.generate_content(model=CHAT_MODEL, contents=QUESTION)

    print(f"Question: {QUESTION}\n")
    print(f"Gemini, with no context:\n{response.text}\n")
    print(
        "Naive RAG (course 1) would embed this question, retrieve the top-k "
        "chunks by cosine similarity, and hand whatever came back straight to "
        "generation, no matter how relevant those chunks actually were. "
        "Lesson 2 shows this happening for real: naive retrieval will "
        "confidently return the weather-station note (same project, same "
        "hardware, same vocabulary) even though the actual answer lives in "
        "a different note entirely. Nothing in that pipeline notices, "
        "generation just gets handed the wrong context and does its best.\n"
    )
    print(
        "Corrective RAG (Yan et al. 2024, 'Corrective Retrieval Augmented "
        "Generation', arXiv:2401.15884) adds exactly the step naive RAG is "
        "missing: a retrieval evaluator that grades each retrieved chunk's "
        "confidence (correct / ambiguous / incorrect), refines the chunks "
        "worth keeping, and falls back to external web search for the ones "
        "graded incorrect."
    )
    print("\nTwo simplifications this course makes early on, closed later:")
    print(
        "  1. Beginner's rewrite-and-re-retrieve loop (Lessons 6-7) queries "
        "the SAME internal corpus again. The paper's actual 'incorrect' "
        "response is external web search - built properly in Lesson 22."
    )
    print(
        "  2. Beginner grades chunks as a binary relevant / not-relevant "
        "call (Lesson 3). The paper's full three-way correct / ambiguous / "
        "incorrect confidence grade arrives in Lesson 12, once strip-level "
        "refinement (Lessons 10-11) exists to act on 'ambiguous'."
    )


if __name__ == "__main__":
    main()
