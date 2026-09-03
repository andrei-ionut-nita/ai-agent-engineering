"""
Lesson 19: timing the one-time cost of captioning vs. the recurring cost
of re-attaching an image at generation time.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/03_advanced/19_where_per_query_captioning_gets_expensive/lesson.py
"""

import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"

IMAGES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "images"
IMAGE_PATH = IMAGES_DIR / "derailleur-hanger-diagram.png"

CAPTION_PROMPT = (
    "Describe this image in detail, for someone who cannot see it. "
    "Include any text, numbers, labels, or colors visible in the image, "
    "exactly as shown. Be specific and factual, do not guess at anything "
    "not visible."
)
QUESTION = "What's the torque spec printed on this part, and what color is it printed in?"


def caption_image(image_path: Path) -> str:
    image_bytes = image_path.read_bytes()
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=[image_part, CAPTION_PROMPT],
    )
    return response.text or ""


def generate_answer_with_image(image_path: Path, query: str) -> str:
    image_bytes = image_path.read_bytes()
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    response = client.models.generate_content(model=CHAT_MODEL, contents=[image_part, query])
    return response.text or ""


def time_caption_only(image_path: Path) -> float:
    start = time.perf_counter()
    caption_image(image_path)
    return time.perf_counter() - start


def time_generation_with_image(image_path: Path, query: str) -> float:
    start = time.perf_counter()
    generate_answer_with_image(image_path, query)
    return time.perf_counter() - start


def main() -> None:
    caption_time = time_caption_only(IMAGE_PATH)
    generation_time = time_generation_with_image(IMAGE_PATH, QUESTION)

    print(f"Captioning (paid once): {caption_time:.4f}s")
    print(f"Generation with re-attached image (paid per retrieval): {generation_time:.4f}s\n")

    retrievals_per_day = 100
    print(f"If this image is retrieved {retrievals_per_day} times/day:")
    print(f"  Captioning cost (one-time):      {caption_time:.4f}s total")
    print(f"  Re-attachment cost (cumulative): {generation_time * retrievals_per_day:.4f}s/day")


if __name__ == "__main__":
    main()
