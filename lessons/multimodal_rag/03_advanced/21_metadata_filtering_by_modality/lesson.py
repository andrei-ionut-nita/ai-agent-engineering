"""
Lesson 21: narrowing a chromadb query to one modality with a where filter.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/03_advanced/21_metadata_filtering_by_modality/lesson.py
"""

from pathlib import Path

import chromadb
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


def build_collection() -> chromadb.Collection:
    note_paths = sorted(NOTES_DIR.glob("*.md"))
    note_texts = [path.read_text() for path in note_paths]
    note_vectors = embed_texts(note_texts)

    image_paths = sorted(IMAGES_DIR.glob("*.png"))
    captions = [caption_image(path) for path in image_paths]
    caption_vectors = embed_texts(captions)

    ids = [p.name for p in note_paths] + [p.name for p in image_paths]
    documents = note_texts + captions
    embeddings = note_vectors + caption_vectors
    metadatas = [{"modality": "text", "source": p.name} for p in note_paths] + [
        {"modality": "image", "source": p.name} for p in image_paths
    ]

    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="mixed")
    collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
    return collection


def query_collection(
    collection: chromadb.Collection,
    query_vector: list[float],
    n_results: int,
    modality: str | None = None,
) -> dict:
    # None means "no filter, search everything"; naive_rag Lesson 22's
    # exact pattern, applied to "modality" instead of "source"/"area".
    where = {"modality": modality} if modality else None
    return collection.query(query_embeddings=[query_vector], n_results=n_results, where=where)


def main() -> None:
    collection = build_collection()

    query = "What does the setup look like?"
    query_vector = embed_texts([query])[0]

    unfiltered = query_collection(collection, query_vector, n_results=1)
    unfiltered_id = unfiltered["ids"][0][0]
    unfiltered_modality = unfiltered["metadatas"][0][0]["modality"]

    filtered = query_collection(collection, query_vector, n_results=1, modality="image")
    filtered_id = filtered["ids"][0][0]
    filtered_modality = filtered["metadatas"][0][0]["modality"]

    print(f"Query: {query!r}\n")
    print(f"Unfiltered top match: {unfiltered_id} (modality={unfiltered_modality})")
    print(f"Filtered to modality='image': {filtered_id} (modality={filtered_modality})")


if __name__ == "__main__":
    main()
