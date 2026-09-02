"""
Lesson 3: grading a single retrieved chunk, relevant or not, with Gemini.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/01_beginner/03_grading_a_retrieved_chunk/lesson.py
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

QUESTION = (
    "Project Aurora's Raspberry Pi writes sensor readings to a SQLite "
    "file on its SD card. Where does that Raspberry Pi physically live "
    "in the house?"
)

# The paper's full grade is a three-way correct/ambiguous/incorrect
# confidence bucket (Lesson 12). This lesson deliberately starts with
# the simpler binary version, a chunk either helps answer the question
# or it doesn't, no confidence shading yet.
GRADE_PROMPT = """You are grading whether a retrieved passage is relevant \
enough to help answer a question. Read the question and the passage, \
then respond with exactly one word: "relevant" or "not_relevant".

Question: {question}

Passage:
{passage}"""


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


def build_vector_store() -> list[dict]:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)
    return [
        {"text": text, "embedding": vector, "source": path.name}
        for path, text, vector in zip(paths, texts, vectors)
    ]


def retrieve(query: str, store: list[dict], k: int) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


def grade_chunk(question: str, chunk_text: str) -> str:
    prompt = GRADE_PROMPT.format(question=question, passage=chunk_text)
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    grade = (response.text or "").strip().lower()
    # Gemini occasionally wraps the word in punctuation or a sentence
    # despite the instruction, this keeps the check forgiving.
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


def main() -> None:
    store = build_vector_store()
    top1 = retrieve(QUESTION, store, k=1)[0]

    print(f"Q: {QUESTION}\n")
    print(f"Top-1 retrieved chunk: {top1['source']} (score={top1['score']:.4f})\n")

    grade = grade_chunk(QUESTION, top1["text"])
    print(f"Grade: {grade}")
    print(
        "\nThe similarity score alone gave no hint this chunk was wrong, "
        "it was the highest-scoring chunk in the store. The grade comes "
        "from a second, independent judgment: does this specific passage "
        "actually contain an answer to this specific question? A high "
        "similarity score and a 'not_relevant' grade can both be true at "
        "the same time, that's the whole point of adding this step."
    )


if __name__ == "__main__":
    main()
