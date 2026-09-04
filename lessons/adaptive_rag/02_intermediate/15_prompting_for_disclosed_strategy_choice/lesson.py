"""
Lesson 15: extending the generation prompt so the final answer discloses,
in its own text, which strategy produced it and why, not just something
this course's harness prints on the side.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/02_intermediate/15_prompting_for_disclosed_strategy_choice/lesson.py
"""

import json
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

Question: {question}"""

CLASSIFY_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={"label": types.Schema(type=types.Type.STRING, enum=LABELS)},
    required=["label"],
)

STRATEGY_REASONS = {
    "naive": "a single, specific fact that one document could directly answer",
    "multi_hop": "a question that named or implied more than one topic, needing facts from two documents combined",
    "corrective": "a vague or cross-cutting question, so retrieval widened its net rather than trusting a single closest match",
}


# The free tier's requests-per-minute limit is easy to hit once a
# single run makes a classify call and a generate call per question. A
# short backoff-and-retry on a 429 keeps this lesson runnable without
# asking you to slow down by hand.
def call_model(**kwargs) -> "types.GenerateContentResponse":
    for attempt in range(5):
        try:
            return client.models.generate_content(**kwargs)
        except ClientError as error:
            if error.code == 429 and attempt < 4:
                time.sleep(20)
                continue
            raise
    raise RuntimeError("Exceeded retries calling the model")


def classify(question: str) -> str:
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
    return json.loads(response.text)["label"]


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


def route(label: str, question: str, store: list[dict]) -> tuple[str, list[dict]]:
    if label == "multi_hop":
        return "multi_hop", retrieve(question, store, k=2)
    if label == "ambiguous":
        return "corrective", retrieve(question, store, k=2)
    return "naive", retrieve(question, store, k=1)


# The system prompt is the extension this lesson is about: two new
# sentences, telling the model to disclose the strategy and the reason
# for it AS PART OF the answer text itself, not as something separate
# this course's own code prints alongside it.
SYSTEM_PROMPT = """You answer questions using only the provided context, \
citing each fact's source document in brackets, e.g. [pizza-dough.md]. \
If the context doesn't contain the answer, say so plainly instead of \
guessing.

End every answer with one final line in exactly this form:
Strategy used: <strategy name> (<one-line reason why this strategy fit this question>)"""


def generate_answer(question: str, strategy: str, retrieved: list[dict]) -> str:
    context = "\n\n".join(f"[Source: {r['source']}]\n{r['text']}" for r in retrieved)
    reason = STRATEGY_REASONS[strategy]
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"The retrieval strategy used for this question was '{strategy}', "
        f"chosen because: {reason}.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )
    response = call_model(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def main() -> None:
    store = build_vector_store()

    questions = [
        "What oven setting does the pizza dough recipe use?",
        "How does wind speed affect things around the house?",
    ]

    for question in questions:
        label = classify(question)
        strategy, retrieved = route(label, question, store)
        answer = generate_answer(question, strategy, retrieved)
        print(f"Q: {question}")
        print(f"A: {answer}\n")

    print(
        "The strategy and the reason for it aren't printed by this "
        "course's own code as a separate line, they're generated inside "
        "the model's own answer text, the last line of A: above. Anyone "
        "reading just the answer, with no access to this script's "
        "internals, can still see which strategy was used and why."
    )


if __name__ == "__main__":
    main()
