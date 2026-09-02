"""
Lesson 6: rewriting the query when every retrieved chunk grades
not-relevant.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/01_beginner/06_query_rewriting/lesson.py
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


def call_model(prompt: str) -> str:
    # The free tier's requests-per-minute limit (15/min for this chat
    # model) is easy to hit once a lesson makes several calls back to
    # back. A short backoff-and-retry on a 429 keeps this lesson
    # runnable without asking you to slow down by hand, Lesson 19 puts
    # a number on why this cost adds up.
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

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

# Genuinely out-of-corpus: none of the five fixture notes say anything
# about France. This is the case Lesson 5's filtering can't fix, every
# retrieved chunk will grade not_relevant no matter which k you pick.
QUESTION = "What is the capital of France?"
K = 3

GRADE_PROMPT = """You are grading whether a retrieved passage is relevant \
enough to help answer a question. Read the question and the passage, \
then respond with exactly one word: "relevant" or "not_relevant".

Question: {question}

Passage:
{passage}"""

REWRITE_PROMPT = """The question below was just asked against a small \
personal notes collection (topics: a home weather station, a garden, a \
pizza dough recipe, a bookshelf, and cello practice), and none of the \
retrieved passages were relevant. Rewrite the question to be clearer or \
more specific, in case the original wording was the problem. Reply with \
only the rewritten question, nothing else.

Original question: {question}"""


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
    grade = call_model(prompt).strip().lower()
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


def grade_all(question: str, chunks: list[dict]) -> list[dict]:
    return [{**chunk, "grade": grade_chunk(question, chunk["text"])} for chunk in chunks]


def rewrite_query(question: str) -> str:
    prompt = REWRITE_PROMPT.format(question=question)
    return call_model(prompt).strip()


def main() -> None:
    store = build_vector_store()
    top_k = retrieve(QUESTION, store, K)
    graded = grade_all(QUESTION, top_k)

    print(f"Q: {QUESTION}\n")
    print(f"Top-{K}, graded:")
    for chunk in graded:
        print(f"  {chunk['source']} (score={chunk['score']:.4f}): {chunk['grade']}")

    all_not_relevant = all(chunk["grade"] == "not_relevant" for chunk in graded)
    print(f"\nAll graded not-relevant: {all_not_relevant}")

    if all_not_relevant:
        rewritten = rewrite_query(QUESTION)
        print(f"\nRewritten query: {rewritten!r}")
        print(
            "\nLesson 7 re-retrieves with this rewritten query. Worth "
            "noticing now: rewriting can fix a *poorly worded* question "
            "against a corpus that does contain the answer, but it cannot "
            "manufacture an answer that was never in the corpus to begin "
            "with. 'What is the capital of France?' isn't badly worded, "
            "it's simply not something these five notes can answer, no "
            "rephrasing changes that. That gap is exactly what Lesson 22's "
            "real external-search branch is for."
        )


if __name__ == "__main__":
    main()
