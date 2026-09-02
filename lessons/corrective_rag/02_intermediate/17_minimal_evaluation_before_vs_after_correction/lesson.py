"""
Lesson 17: precision@k before vs. after correction, plus a small
end-to-end answer-quality check.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/02_intermediate/17_minimal_evaluation_before_vs_after_correction/lesson.py
"""

import math
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

# The same labeled evaluation set shape as naive_rag Lesson 17, plus one
# addition: the first question is this course's running example, the
# one naive top-1 retrieval confidently gets wrong (Lesson 2). The other
# four are unambiguous, naive retrieval already handles them correctly.
LABELED_QUESTIONS = [
    (
        "Project Aurora's Raspberry Pi writes sensor readings to a SQLite "
        "file on its SD card. Where does that Raspberry Pi physically "
        "live in the house?",
        "bookshelf.md",
    ),
    ("How often does the wind speed sensor need re-oiling?", "weather-station.md"),
    ("What's the cold ferment time for the pizza dough?", "pizza-dough.md"),
    ("What piece is being practiced on the cello?", "cello-practice.md"),
    ("Which vegetables grow in the second raised bed?", "garden.md"),
]

GRADE_PROMPT = """You are grading whether a retrieved passage is relevant \
enough to help answer a question. Respond with exactly one word: \
"relevant" or "not_relevant".

Question: {question}

Passage:
{passage}"""


def call_model(prompt: str) -> str:
    for attempt in range(5):
        try:
            response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
            return response.text or ""
        except ClientError as error:
            if error.code == 429 and attempt < 4:
                time.sleep(20)
                continue
            raise
    raise RuntimeError("Exceeded retries calling the model")


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    assert response.embeddings is not None
    return [e.values for e in response.embeddings]  # type: ignore[misc]


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


def retrieve_by_vector(query_vector: list[float], store: list[dict], k: int) -> list[dict]:
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


def grade_chunk(question: str, chunk_text: str) -> str:
    prompt = GRADE_PROMPT.format(question=question, passage=chunk_text)
    grade = call_model(prompt).strip().lower()
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


def generate_answer(query: str, chunks: list[dict]) -> str:
    if not chunks:
        return "I don't have any information relevant to that question."
    context = "\n\n---\n\n".join(c["text"] for c in chunks)
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {query}"""
    return call_model(prompt)


def precision_before(store: list[dict], query_vectors: list[list[float]]) -> float:
    hits = 0
    for (question, expected_source), qv in zip(LABELED_QUESTIONS, query_vectors):
        top1 = retrieve_by_vector(qv, store, k=1)[0]
        hit = top1["source"] == expected_source
        hits += hit
        print(f"  [{'HIT ' if hit else 'MISS'}] {question!r} -> expected {expected_source}, got {top1['source']}")
    return hits / len(LABELED_QUESTIONS)


def precision_after(store: list[dict], query_vectors: list[list[float]]) -> float:
    hits = 0
    for (question, expected_source), qv in zip(LABELED_QUESTIONS, query_vectors):
        # Correction: over-fetch k=3, grade every candidate, keep what's
        # relevant. This is Lessons 4-5's pipeline, unchanged.
        top3 = retrieve_by_vector(qv, store, k=3)
        relevant_sources = [c["source"] for c in top3 if grade_chunk(question, c["text"]) == "relevant"]
        hit = expected_source in relevant_sources
        hits += hit
        print(f"  [{'HIT ' if hit else 'MISS'}] {question!r} -> expected {expected_source}, got {relevant_sources}")
    return hits / len(LABELED_QUESTIONS)


def main() -> None:
    store = build_vector_store()
    questions = [q for q, _ in LABELED_QUESTIONS]
    query_vectors = embed_texts(questions)

    print("precision@1, BEFORE correction (naive top-1 only):")
    before_score = precision_before(store, query_vectors)
    print(f"  Score: {before_score:.2f} ({int(before_score * len(LABELED_QUESTIONS))}/{len(LABELED_QUESTIONS)})\n")

    print("precision@1-equivalent, AFTER correction (over-fetch k=3, grade, filter):")
    after_score = precision_after(store, query_vectors)
    print(f"  Score: {after_score:.2f} ({int(after_score * len(LABELED_QUESTIONS))}/{len(LABELED_QUESTIONS)})\n")

    # End-to-end answer-quality check: does the FINAL GENERATED ANSWER
    # actually improve on the one question naive retrieval got wrong,
    # not just retrieval precision. This is the check naive_rag's own
    # Lesson 17 doesn't do, and this course's L1 premise rests on
    # generation actually improving, not just a retrieval metric.
    hard_question, expected_source = LABELED_QUESTIONS[0]
    naive_top1 = retrieve_by_vector(query_vectors[0], store, k=1)
    naive_answer = generate_answer(hard_question, naive_top1)

    top3 = retrieve_by_vector(query_vectors[0], store, k=3)
    corrected_chunks = [c for c in top3 if grade_chunk(hard_question, c["text"]) == "relevant"]
    corrected_answer = generate_answer(hard_question, corrected_chunks)

    print(f"Answer quality check on: {hard_question!r}")
    print(f"  Naive answer:     {naive_answer}")
    print(f"  Corrected answer: {corrected_answer}")


if __name__ == "__main__":
    main()
