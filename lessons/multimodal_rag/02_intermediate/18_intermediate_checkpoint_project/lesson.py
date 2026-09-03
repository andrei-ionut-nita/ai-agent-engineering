"""
Lesson 18: Intermediate Checkpoint - Notes-and-Diagrams Search Assistant.

No new concepts, this combines Lessons 10-17 into one small script.
Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/02_intermediate/18_intermediate_checkpoint_project/lesson.py
"""

import math
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pypdf import PdfReader

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

DOCUMENT_FIGURES = {
    "home-observatory.md": ["observatory-finder-scope.png", "observatory-mount-wiring.png"],
    "sourdough-starter.md": ["starter-jar-markings.png"],
    "bike-repair.md": ["derailleur-hanger-diagram.png"],
}


def caption_image_bytes(image_bytes: bytes, mime_type: str) -> str:
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
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


def extract_images_from_pdf(pdf_path: Path) -> list[bytes]:
    reader = PdfReader(pdf_path)
    return [image_file.data for image_file in reader.pages[0].images]


def build_text_records() -> list[dict]:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)
    return [
        {"text": text, "embedding": vector, "source": path.name, "modality": "text", "image_path": None}
        for path, text, vector in zip(paths, texts, vectors)
    ]


def build_figure_records() -> list[dict]:
    records = []
    for document_name, image_names in DOCUMENT_FIGURES.items():
        for figure_number, image_name in enumerate(image_names, start=1):
            image_path = IMAGES_DIR / image_name
            caption = caption_image_bytes(image_path.read_bytes(), "image/png")
            records.append(
                {
                    "text": caption,
                    "source": image_name,
                    "modality": "image",
                    "image_path": image_path,
                    "parent_document": document_name,
                    "figure_number": figure_number,
                }
            )
    return records


def build_pdf_records() -> list[dict]:
    pdf_path = IMAGES_DIR / "circuit-board-notebook.pdf"
    records = []
    for figure_number, image_bytes in enumerate(extract_images_from_pdf(pdf_path), start=1):
        caption = caption_image_bytes(image_bytes, "image/jpeg")
        records.append(
            {
                "text": caption,
                "source": f"{pdf_path.name} (page 1)",
                "modality": "image",
                "image_path": None,  # already extracted; no standalone file to re-read
                "image_bytes": image_bytes,
                "parent_document": "circuit-board.md",
                "figure_number": figure_number,
            }
        )
    return records


def build_mixed_store() -> list[dict]:
    text_records = build_text_records()
    image_records = build_figure_records() + build_pdf_records()
    vectors = embed_texts([r["text"] for r in image_records])
    for record, vector in zip(image_records, vectors):
        record["embedding"] = vector
    return text_records + image_records


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def retrieve_balanced(query: str, store: list[dict], k_text: int, k_image: int) -> list[dict]:
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


def build_context_label(record: dict) -> str:
    if record["modality"] == "image":
        return f"an image ({record['source']}, fig. {record.get('figure_number', 1)})"
    return f"a text note ({record['source']})"


def generate_answer(query: str, retrieved: list[dict]) -> str:
    parts: list[types.Part | str] = []
    for record in retrieved:
        label = build_context_label(record)
        if record["modality"] == "image":
            image_bytes = (
                record["image_path"].read_bytes()
                if record.get("image_path") is not None
                else record["image_bytes"]
            )
            mime_type = "image/png" if record.get("image_path") is not None else "image/jpeg"
            parts.append(f"[Source: {label}]")
            parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
        else:
            parts.append(f"[Source: {label}]\n{record['text']}")

    parts.append(
        f"""Question: {query}

Rules:
- Every claim must cite its source, including whether it came from a text note or an image, like this: (according to the image derailleur-hanger-diagram.png).
- If the context above doesn't contain the answer, say so, don't guess."""
    )
    response = client.models.generate_content(model=CHAT_MODEL, contents=parts)
    return response.text or ""


def ask(query: str, store: list[dict], k_text: int = 2, k_image: int = 1) -> str:
    retrieved = retrieve_balanced(query, store, k_text, k_image)
    return generate_answer(query, retrieved)


def main() -> None:
    store = build_mixed_store()
    print(f"Indexed {len(store)} records\n")

    questions = [
        "How often does the chain and cassette get replaced on the commuter bike?",
        "What's the torque spec printed on the derailleur hanger, and in what color?",
        "What frequency was measured on the 555 timer's pin 3 output?",
    ]
    for question in questions:
        print(f"Q: {question}")
        print(f"A: {ask(question, store)}\n")


if __name__ == "__main__":
    main()
