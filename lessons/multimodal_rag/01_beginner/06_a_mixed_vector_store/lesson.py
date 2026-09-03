"""
Lesson 6: text chunks and image captions, combined into one list.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/01_beginner/06_a_mixed_vector_store/lesson.py
"""

from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"
IMAGES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "images"

CAPTION_PROMPT = (
    "Describe this image in detail, for someone who cannot see it. "
    "Include any text, numbers, labels, or colors visible in the image, "
    "exactly as shown. Be specific and factual, do not guess at anything "
    "not visible."
)


def caption_image(image_path: Path) -> str:
    image_bytes = image_path.read_bytes()
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=[image_part, CAPTION_PROMPT],
    )
    return response.text or ""


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    assert response.embeddings is not None
    result = []
    for embedding in response.embeddings:
        assert embedding.values is not None
        result.append(embedding.values)
    return result


def build_text_records() -> list[dict]:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)
    return [
        {"text": text, "embedding": vector, "source": path.name, "image_path": None}
        for path, text, vector in zip(paths, texts, vectors)
    ]


def build_image_records() -> list[dict]:
    paths = sorted(IMAGES_DIR.glob("*.png"))
    captions = [caption_image(path) for path in paths]
    vectors = embed_texts(captions)
    return [
        {"text": caption, "embedding": vector, "source": path.name, "image_path": path}
        for path, caption, vector in zip(paths, captions, vectors)
    ]


def build_mixed_store() -> list[dict]:
    # One plain list, two sources of records. Nothing about the shape
    # of a record marks it as "text" or "image", that's on purpose,
    # see README.md.
    return build_text_records() + build_image_records()


def main() -> None:
    text_records = build_text_records()
    image_records = build_image_records()
    store = text_records + image_records

    print(f"Text records: {len(text_records)} ({', '.join(r['source'] for r in text_records)})")
    print(f"Image records: {len(image_records)} ({', '.join(r['source'] for r in image_records)})")
    print(f"Mixed store: {len(store)} records total")


if __name__ == "__main__":
    main()
