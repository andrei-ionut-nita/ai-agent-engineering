"""
Lesson 21: bounding the rewrite-and-re-retrieve loop with a
max-attempts guard, instead of retrying forever.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/03_advanced/21_bounding_correction_loops/lesson.py
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

MAX_REWRITE_ATTEMPTS = 2

GRADE_PROMPT = """You are grading whether a retrieved passage is relevant \
enough to help answer a question. Respond with exactly one word: \
"relevant" or "not_relevant".

Question: {question}

Passage:
{passage}"""

REWRITE_PROMPT = """The question below was just asked against a small \
personal notes collection (topics: a home weather station, a garden, a \
pizza dough recipe, a bookshelf, and cello practice), and none of the \
retrieved passages were relevant{previous_attempts}. Rewrite the \
question, trying a genuinely different angle than any previous attempt. \
Reply with only the rewritten question.

Original question: {question}"""


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


def bounded_corrective_ask(query: str, store: list[dict], k: int = 3) -> str:
    current_query = query
    previous_attempts: list[str] = []

    for attempt in range(MAX_REWRITE_ATTEMPTS + 1):
        retrieved = retrieve(current_query, store, k)
        relevant = [c for c in retrieved if grade_chunk(current_query, c["text"]) == "relevant"]
        print(f"  attempt {attempt}: query={current_query!r} -> {len(relevant)} relevant chunk(s)")

        if relevant:
            context = "\n\n---\n\n".join(c["text"] for c in relevant)
            prompt = f"""Answer the question using only the context below.

Context:
{context}

Question: {current_query}"""
            return call_model(prompt)

        if attempt == MAX_REWRITE_ATTEMPTS:
            break

        previous_attempts.append(current_query)
        attempts_note = "" if not previous_attempts[1:] else f" (previous rewrite also failed: {previous_attempts[-1]!r})"
        current_query = call_model(REWRITE_PROMPT.format(question=query, previous_attempts=attempts_note)).strip()

    return (
        f"I don't have any information relevant to that question, after "
        f"{MAX_REWRITE_ATTEMPTS} rewrite attempt(s), nothing relevant was found."
    )


def main() -> None:
    store = build_vector_store()

    # Out of corpus, no rewrite will ever find it, this is exactly the
    # case the bound exists for: without one, a system might keep
    # rewriting and re-retrieving indefinitely, burning calls on a
    # question the corpus was never going to answer.
    question = "What is the capital of France?"
    print(f"Q: {question}  (max {MAX_REWRITE_ATTEMPTS} rewrite attempts)\n")
    answer = bounded_corrective_ask(question, store)
    print(f"\nFinal answer: {answer}")


if __name__ == "__main__":
    main()
