"""
Lesson 22: external web search as the paper's actual "incorrect"
branch, replacing Lessons 6-7's internal rewrite-and-retry with the
real corrective action from Yan et al. 2024.

This is what "Corrective RAG" means in the literature, not the internal
rewrite loop Lessons 6-7 built. That loop was an explicitly named
simplification (Lesson 1), this lesson closes the gap it left open.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/03_advanced/22_external_web_search_as_the_incorrect_branch/lesson.py
"""

import math
import time
from pathlib import Path
from typing import Callable

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


def retrieve(query: str, store: list[dict], k: int) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


def grade_chunk(question: str, chunk_text: str) -> str:
    grade = call_model(GRADE_PROMPT.format(question=question, passage=chunk_text)).strip().lower()
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


# A tiny mock "web search index", standing in for a real search API.
# The point of this lesson is the pluggable SHAPE (a function that takes
# a query and returns text or None), not any particular provider,
# swapping this out for a real search API (Tavily, Bing, Google
# Programmable Search, whatever's available) requires no other code in
# this file to change, only this one function's body.
_MOCK_WEB_INDEX = {
    "capital of france": "Paris is the capital and most populous city of France.",
}


def mock_web_search(query: str) -> str | None:
    query_lower = query.lower()
    for keyword, result in _MOCK_WEB_INDEX.items():
        if keyword in query_lower:
            return result
    return None


# The pluggable interface: any function matching this signature can
# stand in here, this lesson wires in the mock above by default so the
# whole course keeps running with only GOOGLE_API_KEY, no external
# search API key required.
ExternalSearch = Callable[[str], "str | None"]


def corrective_ask_with_external_fallback(
    query: str,
    store: list[dict],
    external_search: ExternalSearch,
    k: int = 3,
) -> str:
    retrieved = retrieve(query, store, k)
    relevant = [c for c in retrieved if grade_chunk(query, c["text"]) == "relevant"]

    if relevant:
        context = "\n\n---\n\n".join(c["text"] for c in relevant)
        source_note = "the notes collection"
    else:
        # This is the real "incorrect" branch (Yan et al. 2024), not
        # Lessons 6-7's internal rewrite: every internal chunk graded
        # not-relevant, so fall back to an entirely different knowledge
        # source instead of asking the same corpus again.
        web_result = external_search(query)
        if web_result is None:
            return "I don't have any information relevant to that question, internally or externally."
        context = web_result
        source_note = "external web search"

    prompt = f"""Answer the question using only the context below, and \
mention where the context came from ({source_note}).

Context:
{context}

Question: {query}"""
    return call_model(prompt)


def main() -> None:
    store = build_vector_store()

    for question in (
        "How often does the wind speed sensor need re-oiling?",  # internal
        "What is the capital of France?",  # external
    ):
        print(f"Q: {question}")
        answer = corrective_ask_with_external_fallback(question, store, mock_web_search)
        print(f"A: {answer}\n")

    print(
        "The first question resolves entirely from the internal corpus, "
        "the second falls through to external_search() because every "
        "internal chunk graded not-relevant. Swap mock_web_search for a "
        "real search API's client and nothing else in "
        "corrective_ask_with_external_fallback needs to change, the "
        "function signature (query in, text-or-None out) is the whole "
        "contract."
    )


if __name__ == "__main__":
    main()
