"""
Lesson 12: saving captions and embeddings so images aren't re-captioned every run.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/02_intermediate/12_persisting_captions_and_embeddings/lesson.py
"""

import json
import time
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
STORE_PATH = Path(__file__).parent / "store.json"

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


def build_records() -> tuple[list[dict], list[dict]]:
    note_paths = sorted(NOTES_DIR.glob("*.md"))
    note_texts = [path.read_text() for path in note_paths]
    note_vectors = embed_texts(note_texts)
    text_records = [
        {"text": text, "embedding": vector, "source": path.name, "modality": "text", "image_path": None}
        for path, text, vector in zip(note_paths, note_texts, note_vectors)
    ]

    image_paths = sorted(IMAGES_DIR.glob("*.png"))
    captions = [caption_image(path) for path in image_paths]
    caption_vectors = embed_texts(captions)
    image_records = [
        {"text": caption, "embedding": vector, "source": path.name, "modality": "image", "image_path": path}
        for path, caption, vector in zip(image_paths, captions, caption_vectors)
    ]

    return text_records, image_records


def save_store(store: list[dict], path: Path) -> None:
    # Path objects aren't JSON-serializable; convert to a plain string
    # (or keep None) before writing, everything else round-trips as-is.
    serializable = [
        {**record, "image_path": str(record["image_path"]) if record["image_path"] else None}
        for record in store
    ]
    path.write_text(json.dumps(serializable))


def load_store(path: Path) -> list[dict]:
    records = json.loads(path.read_text())
    for record in records:
        if record["image_path"] is not None:
            record["image_path"] = Path(record["image_path"])
    return records


def main() -> None:
    if STORE_PATH.exists():
        start = time.perf_counter()
        store = load_store(STORE_PATH)
        elapsed = time.perf_counter() - start
        print(f"Loaded {len(store)} records from {STORE_PATH.name} in {elapsed:.4f}s")
        print("(no captioning or embedding calls made, delete store.json to force a rebuild)")
    else:
        start = time.perf_counter()
        text_records, image_records = build_records()
        store = text_records + image_records
        elapsed = time.perf_counter() - start
        save_store(store, STORE_PATH)
        print(
            f"Captioned {len(image_records)} images and embedded {len(store)} "
            f"records in {elapsed:.4f}s, saved to {STORE_PATH.name}"
        )


if __name__ == "__main__":
    main()
