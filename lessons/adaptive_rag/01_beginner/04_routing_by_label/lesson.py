"""
Lesson 4: given a label, dispatch to one of two retrieval strategies.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/01_beginner/04_routing_by_label/lesson.py
"""

import math
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


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


def classify(question: str) -> Classification:
    prompt = CLASSIFY_PROMPT.format(question=question)
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Classification,
            temperature=0,
        ),
    )
    assert response.text is not None
    return Classification.model_validate_json(response.text)


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


def answer_simple(query: str, store: list[dict]) -> str:
    # naive_rag's own shape, unchanged: one document is enough, so
    # retrieve just the single best match.
    retrieved = retrieve(query, store, k=1)
    return generate_answer(query, retrieved)


def answer_multi_hop(query: str, store: list[dict]) -> str:
    # A lightweight stand-in for graph_rag's real relationship
    # traversal: no entities, no edges, just widening retrieval across
    # every document in the store, so no single top-k cutoff can leave
    # out the one file that happens to carry the second half of the
    # answer, and letting Gemini do the combining. graph_rag's Beginner
    # tier builds the real, entity-and-edge version of "gather facts
    # from more than one place"; this course's own Lesson 21 wires that
    # real implementation in later. Here, "multi-hop" means "retrieve
    # across the whole corpus so no single document has to carry the
    # whole answer alone."
    retrieved = retrieve(query, store, k=len(store))
    return generate_answer(query, retrieved)


def route(question: str, label: str, store: list[dict]) -> str:
    if label == "simple_factual":
        return answer_simple(question, store)
    if label == "multi_hop":
        return answer_multi_hop(question, store)
    raise ValueError(f"No route for label {label!r} yet, that's Lesson 6")


def main() -> None:
    documents = load_documents()
    store = build_vector_store(documents)

    questions = [
        "What oven setting does the pizza dough recipe use?",
        "What two hobbies happen in the same room as the weather station?",
    ]

    for question in questions:
        classification = classify(question)
        answer = route(question, classification.label, store)
        print(f"Q: {question}")
        print(f"  label: {classification.label}")
        print(f"  A: {answer}\n")


if __name__ == "__main__":
    main()
