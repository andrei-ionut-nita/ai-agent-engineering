"""
Lesson 6: a third route, ambiguous -> grade-and-retry, a lightweight
stand-in for corrective_rag's real grading-and-correction pipeline.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/01_beginner/06_adding_a_corrective_route/lesson.py
"""

import math
import time
from pathlib import Path
from typing import Callable

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from pydantic import BaseModel

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


def call_model(prompt: str, **config_kwargs) -> str:
    # The free tier's requests-per-minute limit (15/min for this chat
    # model) is easy to hit once a lesson makes several calls back to
    # back. A short backoff-and-retry on a 429 keeps this lesson
    # runnable without asking you to slow down by hand.
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=CHAT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(**config_kwargs) if config_kwargs else None,
            )
            return response.text or ""
        except ClientError as error:
            if error.code == 429 and attempt < 4:
                time.sleep(20)
                continue
            raise
    raise RuntimeError("Exceeded retries calling the model")


class Classification(BaseModel):
    label: str  # one of: simple_factual, multi_hop, ambiguous
    reason: str


CLASSIFY_PROMPT = """Classify the question below into exactly one of
these three labels:

- simple_factual: answerable from a single fact in a single document,
  no combining of separate documents needed.
- multi_hop: the full answer requires combining facts from two or more
  separate documents, no one document has the whole answer.
- ambiguous: the question is genuinely underspecified, or its answer
  reasonably draws on multiple documents from different angles with no
  single document being clearly the right one to check first.

Question: {question}

Give a one-sentence reason for the label you chose."""

GRADE_PROMPT = """You are grading whether a retrieved passage, by \
itself, fully covers a question, or leaves out related information a \
complete answer would need. Read the question and the passage, then \
respond with exactly one word: "sufficient" or "insufficient".

Question: {question}

Passage:
{passage}"""

BROADEN_PROMPT = """The question below was asked against a small \
personal notes collection (topics: a home weather station, a garden, a \
pizza dough recipe, a bookshelf, and cello practice). A single retrieved \
passage did not fully cover it, likely because the answer is spread \
across more than one note. Rewrite the question to be broader, so a \
wider search is more likely to pull in every note that touches on it. \
Reply with only the rewritten question, nothing else.

Original question: {question}"""


def classify(question: str) -> Classification:
    prompt = CLASSIFY_PROMPT.format(question=question)
    text = call_model(
        prompt,
        response_mime_type="application/json",
        response_schema=Classification,
        temperature=0,
    )
    return Classification.model_validate_json(text)


def load_documents() -> list[dict]:
    paths = sorted(NOTES_DIR.glob("*.md"))
    return [{"text": path.read_text(), "source": path.name} for path in paths]


def embed_texts(texts: list[str]) -> list[list[float]]:
    for attempt in range(5):
        try:
            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=texts,
                config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
            )
            break
        except ClientError as error:
            if error.code == 429 and attempt < 4:
                time.sleep(20)
                continue
            raise
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
    return call_model(prompt)


def grade_chunk(question: str, chunk_text: str) -> str:
    prompt = GRADE_PROMPT.format(question=question, passage=chunk_text)
    grade = call_model(prompt).strip().lower()
    return "sufficient" if "insufficient" not in grade and "sufficient" in grade else "insufficient"


def broaden_query(question: str) -> str:
    prompt = BROADEN_PROMPT.format(question=question)
    return call_model(prompt).strip()


def answer_simple(query: str, store: list[dict]) -> str:
    retrieved = retrieve(query, store, k=1)
    return generate_answer(query, retrieved)


def answer_multi_hop(query: str, store: list[dict]) -> str:
    retrieved = retrieve(query, store, k=len(store))
    return generate_answer(query, retrieved)


def answer_ambiguous(query: str, store: list[dict]) -> str:
    # A lightweight stand-in for corrective_rag's real grade-then-
    # correct pipeline: retrieve narrowly first, grade whether that
    # single chunk actually covers the question, and only pay for a
    # broader retry when the grade says it doesn't. corrective_rag's own
    # Beginner tier builds the real version of this (grading every
    # top-k chunk individually, filtering, rewriting); this is the
    # smallest version that demonstrates the same mechanism: retrieve,
    # grade, retry only if needed.
    first_pass = retrieve(query, store, k=1)
    grade = grade_chunk(query, first_pass[0]["text"])

    if grade == "sufficient":
        return generate_answer(query, first_pass)

    broadened = broaden_query(query)
    second_pass = retrieve(broadened, store, k=len(store))
    return generate_answer(query, second_pass)


STRATEGIES: dict[str, Callable[[str, list[dict]], str]] = {
    "simple_factual": answer_simple,
    "multi_hop": answer_multi_hop,
    "ambiguous": answer_ambiguous,
}


def route(question: str, label: str, store: list[dict]) -> str:
    strategy = STRATEGIES.get(label)
    if strategy is None:
        raise ValueError(f"No route for label {label!r}")
    return strategy(question, store)


def answer(question: str, store: list[dict]) -> tuple[str, str]:
    classification = classify(question)
    result = route(question, classification.label, store)
    return classification.label, result


def main() -> None:
    documents = load_documents()
    store = build_vector_store(documents)

    questions = [
        "What oven setting does the pizza dough recipe use?",
        "What two hobbies happen in the same room as the weather station?",
        # ambiguous: wind speed shows up in weather-station.md (sensor
        # bearings, readings) and garden.md (drying the raised beds), two
        # different angles, no single note is clearly "the" answer.
        "How does wind speed affect things around the house?",
    ]

    for question in questions:
        label, result = answer(question, store)
        print(f"Q: {question}")
        print(f"  label: {label}")
        print(f"  A: {result}\n")


if __name__ == "__main__":
    main()
