"""
Lesson 20: replacing the mixed store's Python list with chromadb.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/03_advanced/20_introducing_chromadb_for_the_mixed_store/lesson.py
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


def build_mixed_store() -> list[dict]:
    note_paths = sorted(NOTES_DIR.glob("*.md"))
    note_texts = [path.read_text() for path in note_paths]
    note_vectors = embed_texts(note_texts)
    text_records = [
        {"text": text, "embedding": vector, "source": path.name, "modality": "text"}
        for path, text, vector in zip(note_paths, note_texts, note_vectors)
    ]

    image_paths = sorted(IMAGES_DIR.glob("*.png"))
    captions = [caption_image(path) for path in image_paths]
    caption_vectors = embed_texts(captions)
    image_records = [
        {"text": caption, "embedding": vector, "source": path.name, "modality": "image"}
        for path, caption, vector in zip(image_paths, captions, caption_vectors)
    ]

    return text_records + image_records


def main() -> None:
    store = build_mixed_store()

    # naive_rag Lesson 20's exact .add() call, with "modality" added
    # alongside "source" as plain metadata.
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="mixed")
    collection.add(
        ids=[record["source"] for record in store],
        documents=[record["text"] for record in store],
        embeddings=[record["embedding"] for record in store],
        metadatas=[{"modality": record["modality"], "source": record["source"]} for record in store],
    )

    query = "What's the torque spec for the derailleur hanger bolt?"
    query_vector = embed_texts([query])[0]

    results = collection.query(query_embeddings=[query_vector], n_results=1)
    ids = results["ids"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    print(f"Collection has {collection.count()} documents\n")
    print(f"Query: {query!r}")
    for doc_id, distance, metadata in zip(ids, distances, metadatas):
        print(f"Top match: {doc_id} (modality={metadata['modality']}, distance={distance:.4f})")


if __name__ == "__main__":
    main()
