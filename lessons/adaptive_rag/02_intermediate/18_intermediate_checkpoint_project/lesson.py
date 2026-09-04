"""
Lesson 18: Intermediate Checkpoint - Notes Assistant That Reports Its
Own Routing.

No new concepts, this combines Lessons 10-17 into one small script.
Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/02_intermediate/18_intermediate_checkpoint_project/lesson.py
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
STORE_PATH = Path(__file__).parent / "store.json"
LOG_PATH = Path(__file__).parent / "routing_log.jsonl"

LABELS = ["simple_factual", "multi_hop", "ambiguous"]

# Lesson 11's threshold: read off Lesson 10's own two observed
# confidence values, not tuned against Lesson 17's evaluation set.
CONFIDENCE_THRESHOLD = 0.92

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

STRATEGY_REASONS = {
    "naive": "a single, specific fact that one document could directly answer",
    "multi_hop": "a question that named or implied more than one topic, needing facts from two documents combined",
    "corrective": "a vague or cross-cutting question, so retrieval widened its net rather than trusting a single closest match",
    "multi_hop (fallback)": "the classifier's own confidence was too low to trust its label, so retrieval widened its net as a safer default",
}


# Lesson 14's cost accounting: a per-call tally, reset before each
# question, so the log entry below can report exactly what one routing
# decision cost, not a running total across the whole session.
CALL_COUNTS = {"embed": 0, "generate": 0}


def reset_counts() -> None:
    CALL_COUNTS["embed"] = 0
    CALL_COUNTS["generate"] = 0


# The free tier's requests-per-minute limit is easy to hit across a run
# that classifies, retrieves, grades, and generates repeatedly. A short
# backoff-and-retry on a 429 keeps this lesson runnable without asking
# you to slow down by hand.
def call_model(**kwargs) -> "types.GenerateContentResponse":
    CALL_COUNTS["generate"] += 1
    for attempt in range(5):
        try:
            return client.models.generate_content(**kwargs)
        except ClientError as error:
            if error.code == 429 and attempt < 4:
                time.sleep(20)
                continue
            raise
    raise RuntimeError("Exceeded retries calling the model")


def embed_texts(texts: list[str]) -> list[list[float]]:
    CALL_COUNTS["embed"] += 1
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


def load_or_build_store() -> list[dict]:
    if STORE_PATH.exists():
        return json.loads(STORE_PATH.read_text())
    store = build_vector_store()
    STORE_PATH.write_text(json.dumps(store))
    return store


def retrieve(query: str, store: list[dict], k: int) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


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


def grade_chunk(question: str, chunk_text: str) -> str:
    prompt = (
        "You are grading whether a retrieved passage is relevant enough "
        "to help answer a question. Respond with exactly one word: "
        '"relevant" or "not_relevant".\n\n'
        f"Question: {question}\n\nPassage:\n{chunk_text}"
    )
    grade = (call_model(model=CHAT_MODEL, contents=prompt).text or "").strip().lower()
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


def route(label: str, confidence: float, question: str, store: list[dict]) -> tuple[str, list[dict]]:
    # Lesson 11's fallback: a low-confidence label isn't trusted enough
    # to route on, fall back to the widest strategy instead.
    if confidence < CONFIDENCE_THRESHOLD:
        return "multi_hop (fallback)", retrieve(question, store, k=2)
    if label == "multi_hop":
        return "multi_hop", retrieve(question, store, k=2)
    if label == "ambiguous":
        scored_all = retrieve(question, store, k=len(store))
        top1 = scored_all[:1]
        if grade_chunk(question, top1[0]["text"]) == "relevant":
            return "corrective", top1
        return "corrective", scored_all[:2]
    return "naive", retrieve(question, store, k=1)


SYSTEM_PROMPT = """You answer questions using only the provided context, \
citing each fact's source document in brackets, e.g. [pizza-dough.md]. \
If the context doesn't contain the answer, say so plainly instead of \
guessing.

End every answer with one final line in exactly this form:
Strategy used: <strategy name> (<one-line reason why this strategy fit this question>)"""


def generate_answer(question: str, strategy: str, retrieved: list[dict]) -> str:
    if not retrieved:
        return "I don't have any information relevant to that question."
    context = "\n\n".join(f"[Source: {r['source']}]\n{r['text']}" for r in retrieved)
    reason = STRATEGY_REASONS[strategy]
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"The retrieval strategy used for this question was '{strategy}', "
        f"chosen because: {reason}.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )
    return call_model(model=CHAT_MODEL, contents=prompt).text or ""


def log_decision(entry: dict) -> None:
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def ask(query: str, store: list[dict], k: int = 2) -> str:
    reset_counts()
    label, confidence = classify_with_confidence(query)
    strategy, retrieved = route(label, confidence, query, store)
    answer = generate_answer(query, strategy, retrieved)
    log_decision(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "question": query,
            "label": label,
            "confidence": confidence,
            "strategy": strategy,
            "sources_retrieved": [r["source"] for r in retrieved],
            "embed_calls": CALL_COUNTS["embed"],
            "generate_calls": CALL_COUNTS["generate"],
        }
    )
    return answer


def main() -> None:
    store = load_or_build_store()
    print(f"Notes index ready: {len(store)} documents\n")

    questions = [
        "What oven setting does the pizza dough recipe use?",
        "What two hobbies happen in the same room as the weather station?",
        "How does wind speed affect things around the house?",
    ]

    for question in questions:
        answer = ask(question, store)
        print(f"Q: {question}")
        print(f"A: {answer}\n")

    print(f"--- {LOG_PATH.name} ---")
    for line in LOG_PATH.read_text().splitlines()[-len(questions):]:
        print(line)


if __name__ == "__main__":
    main()
