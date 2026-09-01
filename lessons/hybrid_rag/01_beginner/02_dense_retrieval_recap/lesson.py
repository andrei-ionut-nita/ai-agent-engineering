"""
Lesson 2: dense retrieval, recapped in one script (embed, rank, generate).

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/01_beginner/02_dense_retrieval_recap/lesson.py
"""

import math
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"
EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

# One paraphrase-friendly question: no shared keywords with the document
# it answers, dense retrieval's home turf.
QUESTION = "Why does my espresso taste weak and sour lately?"


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    assert response.embeddings is not None
    return [embedding.values for embedding in response.embeddings if embedding.values is not None]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def build_store() -> list[dict]:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)
    return [
        {"text": text, "embedding": vector, "source": path.name}
        for path, text, vector in zip(paths, texts, vectors)
    ]


def retrieve(query_vector: list[float], store: list[dict], k: int = 2) -> list[dict]:
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


def generate(question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(f"[{c['source']}]\n{c['text']}" for c in chunks)
    prompt = (
        f"Answer the question using only the context below. Cite the source "
        f"file in brackets.\n\nContext:\n{context}\n\nQuestion: {question}"
    )
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def main() -> None:
    store = build_store()
    query_vector = embed_texts([QUESTION])[0]
    top_chunks = retrieve(query_vector, store, k=2)

    print(f"Question: {QUESTION}\n")
    print("Dense retrieval top-2:")
    for chunk in top_chunks:
        print(f"  {chunk['score']:.4f}  {chunk['source']}")

    answer = generate(QUESTION, top_chunks)
    print(f"\nAnswer:\n{answer}")


if __name__ == "__main__":
    main()
