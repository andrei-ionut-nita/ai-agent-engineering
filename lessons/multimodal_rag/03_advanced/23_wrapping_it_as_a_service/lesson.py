"""
Lesson 23: wrapping ingest() and ask() as a small FastAPI service.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/03_advanced/23_wrapping_it_as_a_service/lesson.py

To run this as a real, live server instead:

    uvicorn lesson:app --reload
"""

from contextlib import asynccontextmanager
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from google import genai
from google.genai import types
from pydantic import BaseModel

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


def ingest(notes_dir: Path, images_dir: Path, chroma_client) -> chromadb.Collection:
    note_paths = sorted(notes_dir.glob("*.md"))
    note_texts = [path.read_text() for path in note_paths]
    note_vectors = embed_texts(note_texts)

    image_paths = sorted(images_dir.glob("*.png"))
    captions = [caption_image(path) for path in image_paths]
    caption_vectors = embed_texts(captions)

    ids = [p.name for p in note_paths] + [p.name for p in image_paths]
    documents = note_texts + captions
    embeddings = note_vectors + caption_vectors
    metadatas = [
        {"modality": "text", "source": p.name, "image_path": ""} for p in note_paths
    ] + [
        {"modality": "image", "source": p.name, "image_path": str(p)} for p in image_paths
    ]

    collection = chroma_client.create_collection(name="mixed")
    collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
    return collection


def ask(query: str, collection: chromadb.Collection, k: int = 2) -> str:
    query_vector = embed_texts([query])[0]
    results = collection.query(
        query_embeddings=[query_vector], n_results=k, include=["documents", "metadatas"]
    )
    documents = results["documents"]
    metadatas = results["metadatas"]
    assert documents is not None and metadatas is not None

    retrieved_documents = documents[0]
    retrieved_metadatas = metadatas[0]
    if not retrieved_documents:
        return "I don't have any information relevant to that question."

    parts: list[types.Part | str] = []
    for document, metadata in zip(retrieved_documents, retrieved_metadatas):
        label = (
            f"an image ({metadata['source']})"
            if metadata["modality"] == "image"
            else f"a text note ({metadata['source']})"
        )
        if metadata["image_path"]:
            image_bytes = Path(metadata["image_path"]).read_bytes()
            parts.append(f"[Source: {label}]")
            parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/png"))
        else:
            parts.append(f"[Source: {label}]\n{document}")

    parts.append(
        f"""Question: {query}

Rules:
- Every claim must cite its source, including whether it came from a text note or an image.
- If the context above doesn't contain the answer, say so, don't guess."""
    )
    response = client.models.generate_content(model=CHAT_MODEL, contents=parts)
    return response.text or ""


class AskResponse(BaseModel):
    answer: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    chroma_client = chromadb.Client()
    app.state.collection = ingest(NOTES_DIR, IMAGES_DIR, chroma_client)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str, k: int = 2) -> AskResponse:
    return AskResponse(answer=ask(q, app.state.collection, k))


def main() -> None:
    with TestClient(app) as test_client:
        for question in (
            "What's the torque spec for the derailleur hanger bolt?",
            "What is the capital of France?",
        ):
            response = test_client.get("/ask", params={"q": question})
            print(f"GET /ask?q={question!r}")
            print(f"  {response.json()}\n")


if __name__ == "__main__":
    main()
