"""
Lesson 1: proving why Multimodal RAG exists, before building it.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/01_beginner/01_what_is_multimodal_rag/lesson.py
"""

from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()

# The raw Gemini client, no LangChain or LlamaIndex in between, the same
# object every lesson in this course talks to Gemini through.
client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"

IMAGES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "images"

# The real answer lives only inside derailleur-hanger-diagram.png (see
# fixtures/README.md), a fact never written down as text anywhere in
# this course's fixtures. This call shows Gemini neither the image nor
# any retrieved context, just the bare question.
QUESTION = (
    "What's the torque spec for the rear derailleur hanger bolt, "
    "and what color is it printed in?"
)


def main() -> None:
    response = client.models.generate_content(model=CHAT_MODEL, contents=QUESTION)

    print(f"Question: {QUESTION}\n")
    print(f"Gemini, with no context and no image:\n{response.text}\n")
    print(
        f"The real answer ('8 Nm, printed in red') lives only inside "
        f"{IMAGES_DIR.name}/derailleur-hanger-diagram.png, an image Gemini "
        "never saw in this call. It either says it doesn't know, or invents "
        "a plausible-sounding number, and no amount of *text*-only RAG over "
        "this course's notes would fix that, the fact was never written "
        "down as text anywhere. Lesson 2 proves that directly.\n"
    )
    print("Multimodal RAG extends Naive RAG's four stages with one new idea:")
    print("  1. Caption  - describe an image in retrievable text (this course's approach)")
    print("  2. Embed    - the caption, with the same pipeline used for text chunks")
    print("  3. Retrieve - text chunks and image captions together, ranked by one query")
    print("  4. Generate - re-attach the *original image* (not just its caption) when it's the best match")


if __name__ == "__main__":
    main()
