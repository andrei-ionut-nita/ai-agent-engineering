"""
Lesson 17: extracting an embedded image from a PDF page before captioning it.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/02_intermediate/17_extracting_images_from_a_pdf/lesson.py
"""

from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pypdf import PdfReader

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"

IMAGES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "images"
PDF_PATH = IMAGES_DIR / "circuit-board-notebook.pdf"

CAPTION_PROMPT = (
    "Describe this image in detail, for someone who cannot see it. "
    "Include any text, numbers, labels, or colors visible in the image, "
    "exactly as shown. Be specific and factual, do not guess at anything "
    "not visible."
)


def caption_image_from_bytes(image_bytes: bytes, mime_type: str) -> str:
    # Same call as caption_image() everywhere else in this course, just
    # taking raw bytes directly instead of reading a standalone file,
    # since a PDF's embedded image has no file of its own on disk.
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=[image_part, CAPTION_PROMPT],
    )
    return response.text or ""


def extract_images_from_pdf(pdf_path: Path) -> list[bytes]:
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    # page.images re-encodes each embedded image, usually as JPEG
    # (image_file.name ends in .jpg); .data is the raw bytes.
    return [image_file.data for image_file in page.images]


def main() -> None:
    images = extract_images_from_pdf(PDF_PATH)
    print(f"{PDF_PATH.name}, page 1: {len(images)} embedded image(s) found\n")

    for image_bytes in images:
        caption = caption_image_from_bytes(image_bytes, mime_type="image/jpeg")
        print(f"Caption:\n{caption}")


if __name__ == "__main__":
    main()
