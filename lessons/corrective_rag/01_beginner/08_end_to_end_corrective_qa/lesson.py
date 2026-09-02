"""
Lesson 8: end-to-end - retrieve, grade, filter or rewrite, re-retrieve,
generate, all in one pipeline.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/01_beginner/08_end_to_end_corrective_qa/lesson.py
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


def generate_answer(query: str, retrieved_chunks: list[dict]) -> str:
    if not retrieved_chunks:
        return "I don't have any information relevant to that question."
    context = "\n\n---\n\n".join(chunk["text"] for chunk in retrieved_chunks)
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {query}"""
    return call_model(prompt)


def corrective_ask(query: str, store: list[dict], k: int = 3) -> str:
    # 1. Retrieve, over-fetched (Lesson 4).
    retrieved = retrieve(query, store, k)
    # 2. Grade every retrieved chunk (Lesson 4).
    graded = grade_all(query, retrieved)
    # 3. Filter to what graded relevant (Lesson 5).
    relevant = [chunk for chunk in graded if chunk["grade"] == "relevant"]

    effective_query = query
    if not relevant:
        # 4. Nothing survived filtering: rewrite and re-retrieve
        #    (Lessons 6-7), once.
        effective_query = rewrite_query(query)
        print(f"    (no relevant chunks, rewrote query to: {effective_query!r})")
        retrieved = retrieve(effective_query, store, k)
        graded = grade_all(effective_query, retrieved)
        relevant = [chunk for chunk in graded if chunk["grade"] == "relevant"]

    # 5. Generate from whatever survived, empty context included
    #    (Lesson 6's honest-failure case falls through to here). Uses
    #    the rewritten wording if a rewrite happened, the clearer
    #    version of the question is also the better one to generate
    #    from, not just to retrieve with.
    return generate_answer(effective_query, relevant)


def main() -> None:
    store = build_vector_store()

    # Two of this course's three running examples, both at the same
    # over-fetched k=3 this pipeline uses by default:
    questions = [
        # Filtering alone fixes this one: the right chunk is retrieved,
        # just outranked (Lessons 2-5), no rewrite needed.
        "Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?",
        # Rewriting fires (every top-3 chunk grades not-relevant) but
        # honestly can't fix it: the corpus just doesn't know (Lesson 6).
        "What is the capital of France?",
    ]

    for question in questions:
        print(f"Q: {question}")
        answer = corrective_ask(question, store)
        print(f"A: {answer}\n")


if __name__ == "__main__":
    main()
