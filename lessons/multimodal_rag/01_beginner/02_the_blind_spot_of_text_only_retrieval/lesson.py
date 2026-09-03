"""
Lesson 2: text-only Naive RAG, still blind to a fact only an image holds.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/01_beginner/02_the_blind_spot_of_text_only_retrieval/lesson.py
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

# Only derailleur-hanger-diagram.png (attached to bike-repair.md) has
# this answer; the note's own text only says "see photo."
QUESTION = (
    "What's the torque spec for the rear derailleur hanger bolt, "
    "and what color is it printed in?"
)


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


def build_vector_store() -> list[dict]:
    # naive_rag's exact pipeline: every note is text, full stop, no
    # notion of an image existing at all.
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)
    return [
        {"text": text, "embedding": vector, "source": path.name}
        for path, text, vector in zip(paths, texts, vectors)
    ]


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


def generate_answer(query: str, retrieved_chunks: list[dict]) -> str:
    context = "\n\n".join(chunk["text"] for chunk in retrieved_chunks)
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {query}"""
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def main() -> None:
    store = build_vector_store()
    retrieved = retrieve(QUESTION, store, k=2)
    answer = generate_answer(QUESTION, retrieved)

    print(f"Question: {QUESTION}\n")
    print(f"Retrieved (text-only): {[r['source'] for r in retrieved]}\n")
    print(f"Answer from text-only RAG:\n{answer}\n")
    print(
        "Retrieval worked correctly, it found the most relevant note. The "
        "note itself just never wrote the answer down as text, only the "
        "image did."
    )


if __name__ == "__main__":
    main()
