"""
Lesson 13: logging every routing decision, question, label, confidence,
and what came of it, to a local append-only JSONL file.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/02_intermediate/13_persisting_routing_decisions/lesson.py
"""

import json
import math
import time
from datetime import datetime, timezone
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
LOG_PATH = Path(__file__).parent / "routing_log.jsonl"

LABELS = ["simple_factual", "multi_hop", "ambiguous"]

CLASSIFY_PROMPT = """You are routing questions to a retrieval strategy \
over a small personal notes collection (documents about a weather \
station, a garden, a pizza dough recipe, a bookshelf, and cello \
practice).

Classify the question below into exactly one label:
- "simple_factual": a specific factual lookup that a single passage in \
ONE document would directly answer (a number, a setting, a schedule). \
This is the default for any concrete, well-scoped question.
- "multi_hop": answering it explicitly requires combining facts that \
live in TWO DIFFERENT documents.
- "ambiguous": the question itself is vague, underspecified, or its \
scope could plausibly span more than one unrelated document without \
the question saying so.

Most well-formed, specific questions are "simple_factual". Only use
"multi_hop" or "ambiguous" when the question clearly demands it.

Also rate your confidence in that label from 0.0 (a coin flip) to 1.0
(certain).

Question: {question}"""

CLASSIFY_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "label": types.Schema(type=types.Type.STRING, enum=LABELS),
        "confidence": types.Schema(type=types.Type.NUMBER),
    },
    required=["label", "confidence"],
)


# The free tier's requests-per-minute limit is easy to hit once a run
# makes several classify and embed calls back to back. A short backoff-
# and-retry on a 429 keeps this lesson runnable without asking you to
# slow down by hand.
def call_model(**kwargs) -> "types.GenerateContentResponse":
    for attempt in range(5):
        try:
            return client.models.generate_content(**kwargs)
        except ClientError as error:
            if error.code == 429 and attempt < 4:
                time.sleep(15)
                continue
            raise
    raise RuntimeError("Exceeded retries calling the model")


def classify_with_confidence(question: str) -> tuple[str, float]:
    prompt = CLASSIFY_PROMPT.format(question=question)
    response = call_model(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CLASSIFY_SCHEMA,
            temperature=0,
        ),
    )
    assert response.text is not None
    result = json.loads(response.text)
    return result["label"], float(result["confidence"])


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
                time.sleep(15)
                continue
            raise
    else:
        raise RuntimeError("Exceeded retries calling the embedding model")
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


def route(label: str, question: str, store: list[dict]) -> tuple[str, list[dict]]:
    if label == "multi_hop":
        return "multi_hop", retrieve(question, store, k=2)
    if label == "ambiguous":
        return "corrective", retrieve(question, store, k=2)
    return "naive", retrieve(question, store, k=1)


def log_decision(entry: dict) -> None:
    # Append-only: one JSON object per line, opened in append mode so
    # every run adds to the log instead of replacing it. This is the
    # simplest durable format for "a growing list of independent
    # records," no need for a database, and unlike a single JSON array
    # a crash mid-write only loses the one unfinished line, not the
    # whole file.
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def route_and_log(question: str, store: list[dict]) -> dict:
    label, confidence = classify_with_confidence(question)
    strategy, retrieved = route(label, question, store)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "label": label,
        "confidence": confidence,
        "strategy": strategy,
        "sources_retrieved": [r["source"] for r in retrieved],
    }
    log_decision(entry)
    return entry


def main() -> None:
    store = build_vector_store()

    if LOG_PATH.exists():
        LOG_PATH.unlink()  # start each demo run from a clean log

    questions = [
        "What oven setting does the pizza dough recipe use?",
        "What two hobbies happen in the same room as the weather station?",
        "How does wind speed affect things around the house?",
    ]

    for question in questions:
        entry = route_and_log(question, store)
        print(f"Q: {entry['question']}")
        print(f"  label: {entry['label']} (confidence={entry['confidence']:.2f})")
        print(f"  strategy: {entry['strategy']}")
        print(f"  sources: {entry['sources_retrieved']}\n")

    print(f"--- {LOG_PATH.name}, {len(questions)} lines ---")
    for line in LOG_PATH.read_text().splitlines():
        print(line)

    print(
        "\nEach line is one complete, independent record: enough to "
        "later ask 'how often did this route to corrective?' or 'what "
        "was the average confidence for multi_hop questions?' without "
        "re-running anything, just by reading this file back."
    )


if __name__ == "__main__":
    main()
