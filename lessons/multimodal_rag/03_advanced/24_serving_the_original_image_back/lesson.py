"""
Lesson 24: returning the actual retrieved image to the caller, not just a description.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/03_advanced/24_serving_the_original_image_back/lesson.py

To run this as a real, live server instead:

    uvicorn lesson:app --reload
"""

from contextlib import asynccontextmanager
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
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


class AskResult(BaseModel):
    answer: str
    source_image: str | None = None


def ask(query: str, collection: chromadb.Collection, k: int = 2) -> AskResult:
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
        return AskResult(answer="I don't have any information relevant to that question.")

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

    # Only the single best-scoring retrieved record decides whether to
    # hand the caller an image filename back, see README.md.
    top_metadata = retrieved_metadatas[0]
    source_image = top_metadata["source"] if top_metadata["modality"] == "image" else None

    return AskResult(answer=response.text or "", source_image=source_image)


@asynccontextmanager
async def lifespan(app: FastAPI):
    chroma_client = chromadb.Client()
    app.state.collection = ingest(NOTES_DIR, IMAGES_DIR, chroma_client)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ask", response_model=AskResult)
def ask_endpoint(q: str, k: int = 2) -> AskResult:
    return ask(q, app.state.collection, k)


@app.get("/image/{filename}")
def get_image(filename: str) -> FileResponse:
    # Validate before touching the filesystem: filename comes straight
    # from the caller, an unchecked path could read any file the
    # process can access.
    image_path = IMAGES_DIR / filename
    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path, media_type="image/png")


def main() -> None:
    with TestClient(app) as test_client:
        for question in (
            "What's the torque spec for the derailleur hanger bolt?",
            "What is the capital of France?",
        ):
            response = test_client.get("/ask", params={"q": question})
            print(f"GET /ask?q={question!r}")
            print(f"  {response.json()}\n")

        image_response = test_client.get("/image/derailleur-hanger-diagram.png")
        print(
            f"GET /image/derailleur-hanger-diagram.png -> "
            f"{image_response.status_code}, {image_response.headers['content-type']}, "
            f"{len(image_response.content)} bytes"
        )


if __name__ == "__main__":
    main()
