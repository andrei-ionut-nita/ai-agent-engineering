"""
Lesson 1: what happens when one fixed retrieval strategy meets a
question it isn't shaped for.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/01_beginner/01_what_is_adaptive_rag/lesson.py
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

# The answer to this question is split across two files: bookshelf.md
# names one hobby (organizing the bookshelf) and confirms the room,
# cello-practice.md names the other hobby and confirms the same room
# again independently. Neither file alone names both hobbies.
QUESTION = "What two hobbies happen in the same room as the weather station?"


def load_documents() -> list[dict]:
    paths = sorted(NOTES_DIR.glob("*.md"))
    return [{"text": path.read_text(), "source": path.name} for path in paths]


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


def build_vector_store(documents: list[dict]) -> list[dict]:
    vectors = embed_texts([document["text"] for document in documents])
    return [{**document, "embedding": vector} for document, vector in zip(documents, vectors)]


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
    context = "\n\n---\n\n".join(chunk["text"] for chunk in retrieved_chunks)
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {query}"""
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def main() -> None:
    documents = load_documents()
    store = build_vector_store(documents)

    print(f"Question: {QUESTION}\n")

    # This is naive_rag's exact retrieve-then-generate shape from that
    # course's own Lesson 8, fixed at k=1, the same shape every question
    # in this course's fixture set gets run through no matter what kind
    # of question it is.
    top1 = retrieve(QUESTION, store, k=1)
    print(f"Naive top-1 retrieval picked: {top1[0]['source']} (score={top1[0]['score']:.4f})\n")

    answer = generate_answer(QUESTION, top1)
    print(f"Answer from one document alone:\n{answer}\n")

    print(
        "Whichever of the two files scored higher this run, the answer "
        "above can only name the hobby that single file mentions, or "
        "admit it doesn't have the other one, because k=1 never gave the "
        "model a chance to see both files together. The question needed "
        "two documents combined; naive top-1 retrieval, by construction, "
        "can only ever hand over one.\n"
    )

    print("This course's roadmap, starting next lesson:")
    print("  1. Classify - label a question's complexity before retrieving anything")
    print("  2. Route    - send that question to the retrieval strategy suited to it")
    print("  3. Retrieve - run that strategy, not always the same one")
    print("  4. Generate - hand the result to Gemini, same as every course before this one")


if __name__ == "__main__":
    main()
