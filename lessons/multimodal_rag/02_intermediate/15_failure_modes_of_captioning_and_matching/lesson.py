"""
Lesson 15: two failures caused by lossy captions and imperfect matching, seen on purpose.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/02_intermediate/15_failure_modes_of_captioning_and_matching/lesson.py
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

IMAGES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "images"

CAPTION_PROMPT = (
    "Describe this image in detail, for someone who cannot see it. "
    "Include any text, numbers, labels, or colors visible in the image, "
    "exactly as shown. Be specific and factual, do not guess at anything "
    "not visible."
)
# Deliberately vague, to isolate what a weaker prompt loses.
WEAK_CAPTION_PROMPT = "Describe this image."


def caption_image(image_path: Path, prompt: str) -> str:
    image_bytes = image_path.read_bytes()
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=[image_part, prompt],
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


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def failure_one_dropped_detail() -> None:
    print("--- Failure 1: a caption that drops a detail ---\n")
    image_path = IMAGES_DIR / "observatory-mount-wiring.png"

    strong_caption = caption_image(image_path, CAPTION_PROMPT)
    weak_caption = caption_image(image_path, WEAK_CAPTION_PROMPT)

    print(f"Strong prompt caption:\n{strong_caption}\n")
    print(f"Weak prompt caption:\n{weak_caption}\n")


def failure_two_caption_matches_image_doesnt() -> None:
    print("--- Failure 2: caption matches, image doesn't answer ---\n")
    image_path = IMAGES_DIR / "starter-jar-markings.png"
    caption = caption_image(image_path, CAPTION_PROMPT)
    caption_vector = embed_texts([caption])[0]

    query = "What jar size (volume) is used for the starter?"
    query_vector = embed_texts([query])[0]
    score = cosine_similarity(query_vector, caption_vector)

    image_bytes = image_path.read_bytes()
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=[
            image_part,
            f"Question: {query}\nAnswer using only what's visible in the image. "
            "If it's not shown, say so plainly.",
        ],
    )

    print(f"Query: {query!r}")
    print(f"Retrieved: {image_path.name} (score={score:.4f})")
    print(f"Answer: {response.text}")


def main() -> None:
    failure_one_dropped_detail()
    failure_two_caption_matches_image_doesnt()


if __name__ == "__main__":
    main()
