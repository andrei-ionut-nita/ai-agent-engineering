"""
Lesson 10: tracking which document (and figure number) each image belongs to.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/02_intermediate/10_captioning_multiple_images_per_document/lesson.py
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

# Hand-maintained figure order per document; order in each list is the
# figure number (fig. 1, fig. 2, ...). Lesson 17 shows a case where
# this mapping comes from a document's own structure instead.
DOCUMENT_FIGURES = {
    "home-observatory.md": ["observatory-finder-scope.png", "observatory-mount-wiring.png"],
    "sourdough-starter.md": ["starter-jar-markings.png"],
    "bike-repair.md": ["derailleur-hanger-diagram.png"],
}


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


def build_image_records() -> list[dict]:
    captions_by_path: dict[Path, str] = {}
    records = []
    for document_name, image_names in DOCUMENT_FIGURES.items():
        for figure_number, image_name in enumerate(image_names, start=1):
            image_path = IMAGES_DIR / image_name
            caption = caption_image(image_path)
            captions_by_path[image_path] = caption
            records.append(
                {
                    "source": image_name,
                    "image_path": image_path,
                    "parent_document": document_name,
                    "figure_number": figure_number,
                    "caption": caption,
                }
            )

    vectors = embed_texts([r["caption"] for r in records])
    for record, vector in zip(records, vectors):
        record["text"] = record.pop("caption")
        record["embedding"] = vector
    return records


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


def main() -> None:
    records = build_image_records()

    print("home-observatory.md has 2 figures:")
    for record in records:
        if record["parent_document"] == "home-observatory.md":
            print(f"  fig. {record['figure_number']}: {record['source']}")

    query = "What color are the motor cables on the mount?"
    top = retrieve(query, records, k=1)[0]
    print(f"\nQuery: {query!r}")
    print(f"Top match: {top['source']} ({top['parent_document']}, fig. {top['figure_number']})")


if __name__ == "__main__":
    main()
