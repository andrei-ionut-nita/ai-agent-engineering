"""
Lesson 16: precision@k on a labeled set mixing text- and image-answerable questions.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/02_intermediate/16_minimal_evaluation_text_vs_image_questions/lesson.py
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

# Deliberately mixes text- and image-answerable questions, unlike
# naive_rag's set, which only ever needed to test text retrieval.
LABELED_QUESTIONS = [
    ("How often does the chain and cassette get replaced?", "bike-repair.md"),
    ("What's the torque spec on the derailleur hanger bolt?", "derailleur-hanger-diagram.png"),
    ("What are the feed and discard fill lines on the starter jar?", "starter-jar-markings.png"),
    ("How fast does the terrarium's condensation clear in a working setup?", "terrarium.md"),
    ("What color are the RA and DEC motor cables?", "observatory-mount-wiring.png"),
]


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


def retrieve_by_vector(query_vector: list[float], store: list[dict], k: int) -> list[dict]:
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


def main() -> None:
    store = build_mixed_store()

    questions = [question for question, _ in LABELED_QUESTIONS]
    query_vectors = embed_texts(questions)

    k = 2
    hits_by_modality: dict[str, list[bool]] = {"text": [], "image": []}

    print(f"precision@{k}:")
    for (question, expected_source), query_vector in zip(LABELED_QUESTIONS, query_vectors):
        retrieved = retrieve_by_vector(query_vector, store, k)
        retrieved_sources = [r["source"] for r in retrieved]
        hit = expected_source in retrieved_sources
        expected_modality = "image" if expected_source.endswith(".png") else "text"
        hits_by_modality[expected_modality].append(hit)

        status = "HIT " if hit else "MISS"
        print(f"  [{status}] {question!r} -> expected {expected_source}, got {retrieved_sources}")

    all_hits = hits_by_modality["text"] + hits_by_modality["image"]
    overall = sum(all_hits) / len(all_hits)
    text_score = sum(hits_by_modality["text"]) / len(hits_by_modality["text"])
    image_score = sum(hits_by_modality["image"]) / len(hits_by_modality["image"])

    print(f"\n  Overall:      {overall:.2f} ({sum(all_hits)}/{len(all_hits)})")
    print(f"  Text-only:    {text_score:.2f} ({sum(hits_by_modality['text'])}/{len(hits_by_modality['text'])})")
    print(f"  Image-only:   {image_score:.2f} ({sum(hits_by_modality['image'])}/{len(hits_by_modality['image'])})")


if __name__ == "__main__":
    main()
