"""
Lesson 6: images and LLM captioning.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/markitdown/02_intermediate/06_images_and_llm_captioning/lesson.py

Lesson 5 skipped office_notice.png because, without an LLM client,
MarkItDown's image converter has nothing to say about a photo beyond
basic metadata. This lesson wires up an LLM client and converts the
same file twice, once without it, once with, so the difference is
visible directly.

MarkItDown's llm_client/llm_model arguments are written for OpenAI's
client interface. Gemini exposes an OpenAI-compatible endpoint, so
this lesson points an OpenAI client at Google's endpoint instead of
OpenAI's, no separate OpenAI account needed, the project's existing
GOOGLE_API_KEY does the authenticating.

This lesson makes one real Gemini API call. Keep that in mind if
you're re-running it repeatedly against a constrained quota.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from markitdown import MarkItDown
from openai import OpenAI

load_dotenv()

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"
IMAGE_PATH = FIXTURES_DIR / "office_notice.png"


def main() -> None:
    # --- Without an LLM client: MarkItDown's image converter can only
    # report what it can determine without understanding pixels, EXIF
    # metadata if present, dimensions, format. This fixture has none of
    # that populated, so the result is nearly empty.
    print("=== Without an LLM client ===\n")
    md_plain = MarkItDown()
    result_plain = md_plain.convert(IMAGE_PATH)
    print(f"Converted length: {len(result_plain.markdown)} characters")
    print(f"Content: {result_plain.markdown!r}\n")

    # --- With an LLM client: MarkItDown sends the image to the model and
    # asks it to describe what it sees, then uses that description as the
    # Markdown content. The client here is OpenAI's SDK, but pointed at
    # Gemini's OpenAI-compatibility endpoint, this is the same pattern
    # used to authenticate against Google's API with this project's
    # existing GOOGLE_API_KEY, no separate OpenAI account required.
    print("=== With an LLM client (Gemini, via OpenAI-compatible endpoint) ===\n")
    client = OpenAI(
        api_key=os.environ["GOOGLE_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    md_llm = MarkItDown(llm_client=client, llm_model="gemini-3.5-flash-lite")
    result_llm = md_llm.convert(IMAGE_PATH)
    print(f"Converted length: {len(result_llm.markdown)} characters")
    print("Content:\n")
    print(result_llm.markdown)


if __name__ == "__main__":
    main()
