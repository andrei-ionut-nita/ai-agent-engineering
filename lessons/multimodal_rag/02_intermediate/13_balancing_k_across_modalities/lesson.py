"""
Lesson 13: ranking each modality separately, so one can't crowd out the other.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/02_intermediate/13_balancing_k_across_modalities/lesson.py
"""

import math
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


def build_mixed_store() -> list[dict]:
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

    return text_records + image_records


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def retrieve(query: str, store: list[dict], k: int) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


def retrieve_balanced(query: str, store: list[dict], k_text: int, k_image: int) -> list[dict]:
    # Rank each modality's own candidates separately, then take a fixed
    # slice from each, guaranteeing a mix instead of hoping plain
    # top-k happens to include both.
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    text_hits = sorted(
        (r for r in scored if r["modality"] == "text"), key=lambda r: r["score"], reverse=True
    )[:k_text]
    image_hits = sorted(
        (r for r in scored if r["modality"] == "image"), key=lambda r: r["score"], reverse=True
    )[:k_image]
    return text_hits + image_hits


def main() -> None:
    store = build_mixed_store()
    query = "What does the closed terrarium look like when it's working correctly?"

    plain = retrieve(query, store, k=3)
    plain_sources = [r["source"] for r in plain]
    plain_images = sum(1 for r in plain if r["modality"] == "image")

    balanced = retrieve_balanced(query, store, k_text=2, k_image=1)
    balanced_sources = [r["source"] for r in balanced]
    balanced_images = sum(1 for r in balanced if r["modality"] == "image")

    print(f"Query: {query!r}\n")
    print(f"Plain top-3 (unbalanced): {plain_sources} ({plain_images} images)")
    print(f"Balanced (k_text=2, k_image=1): {balanced_sources} ({balanced_images} images, guaranteed)")


if __name__ == "__main__":
    main()
