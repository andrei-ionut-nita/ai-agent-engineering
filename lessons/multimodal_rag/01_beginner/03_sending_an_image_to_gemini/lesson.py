"""
Lesson 3: your first multimodal generate_content call.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/01_beginner/03_sending_an_image_to_gemini/lesson.py
"""

from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"

IMAGES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "images"
IMAGE_PATH = IMAGES_DIR / "derailleur-hanger-diagram.png"
QUESTION = "What's the torque spec printed on this part, and what color is it printed in?"


def main() -> None:
    image_bytes = IMAGE_PATH.read_bytes()

    # Part.from_bytes wraps raw image bytes and a MIME type into the
    # same kind of object generate_content already understands for
    # text; this is the confirmed shape for the installed google-genai
    # SDK version (see google/genai/types.py, Part.from_bytes).
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")

    # A plain string in this list is auto-wrapped as a text Part, so
    # mixing an image Part and a string is the normal way to ask a
    # question "about" an attached image.
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=[image_part, QUESTION],
    )

    print(f"Image: {IMAGE_PATH.name}")
    print(f"Question: {QUESTION}\n")
    print(f"Gemini's answer:\n{response.text}")


if __name__ == "__main__":
    main()
