"""
Lesson 4: prompting Gemini to describe an image in retrievable detail.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/01_beginner/04_captioning_an_image/lesson.py
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

# Specific on purpose: a vague caption ("a mechanical diagram") embeds
# close to every other mechanical diagram in the corpus. Asking for
# exact text/numbers/colors, and forbidding guesses, is what makes a
# caption worth retrieving instead of just a label.
CAPTION_PROMPT = (
    "Describe this image in detail, for someone who cannot see it. "
    "Include any text, numbers, labels, or colors visible in the image, "
    "exactly as shown. Be specific and factual, do not guess at anything "
    "not visible."
)


def caption_image(image_path: Path) -> str:
    # This is Lesson 3's call, generalized: this function is the one
    # new building block this course adds on top of naive_rag's
    # pipeline, reused unchanged from here through the capstone.
    image_bytes = image_path.read_bytes()
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=[image_part, CAPTION_PROMPT],
    )
    return response.text or ""


def main() -> None:
    print(f"Captioning {IMAGE_PATH.name}...\n")
    caption = caption_image(IMAGE_PATH)
    print(f"Caption:\n{caption}")


if __name__ == "__main__":
    main()
