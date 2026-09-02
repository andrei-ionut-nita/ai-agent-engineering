"""
Lesson 18: Intermediate Checkpoint - Notes Search With a "Corrected"
Indicator and Citations.

No new concepts, this combines Lessons 10-17 into one small script.
Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/02_intermediate/18_intermediate_checkpoint_project/lesson.py
"""

import math
import re
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
K = 3

CONFIDENCE_PROMPT = """You are a strict retrieval evaluator. Grade how \
confident you are that the passage below contains a clear, direct \
answer to the question. Choose exactly one: "correct", "ambiguous", or \
"incorrect". Respond with exactly one word.

Question: {question}

Passage:
{passage}"""

STRIP_GRADE_PROMPT = """You are grading whether a single sentence is \
relevant enough to help answer a question. Respond with exactly one \
word: "relevant" or "not_relevant".

Question: {question}

Sentence:
{sentence}"""

REWRITE_PROMPT = """The question below was just asked against a small \
personal notes collection (topics: a home weather station, a garden, a \
pizza dough recipe, a bookshelf, and cello practice), and none of the \
retrieved passages were relevant. Rewrite the question to be clearer or \
more specific. Reply with only the rewritten question.

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


def grade_confidence(question: str, passage: str) -> str:
    grade = call_model(CONFIDENCE_PROMPT.format(question=question, passage=passage)).strip().lower()
    for bucket in ("incorrect", "ambiguous", "correct"):
        if bucket in grade:
            return bucket
    return "incorrect"


def split_into_strips(text: str) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    strips = []
    for paragraph in paragraphs:
        strips.extend(s.strip() for s in re.split(r"(?<=[.!?])\s+", paragraph) if s.strip())
    return strips


def grade_strip(question: str, strip: str) -> str:
    grade = call_model(STRIP_GRADE_PROMPT.format(question=question, sentence=strip)).strip().lower()
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


def refine(question: str, chunk_text: str) -> str:
    strips = split_into_strips(chunk_text)
    relevant = [s for s in strips if grade_strip(question, s) == "relevant"]
    # If nothing survives strip-level refinement (Lesson 12's honest
    # "ambiguous but nothing usable" outcome), fall back to the whole
    # chunk rather than handing generation an empty context.
    return " ".join(relevant) if relevant else chunk_text


def ask(query: str, store: list[dict], k: int = K) -> tuple[str, bool]:
    retrieved = retrieve(query, store, k)
    naive_top1_source = retrieved[0]["source"] if retrieved else None

    graded = [{**c, "confidence": grade_confidence(query, c["text"])} for c in retrieved]
    kept = [c for c in graded if c["confidence"] in ("correct", "ambiguous")]

    effective_query = query
    if not kept:
        effective_query = call_model(REWRITE_PROMPT.format(question=query)).strip()
        retrieved = retrieve(effective_query, store, k)
        graded = [{**c, "confidence": grade_confidence(effective_query, c["text"])} for c in retrieved]
        kept = [c for c in graded if c["confidence"] in ("correct", "ambiguous")]

    used_sources = {c["source"] for c in kept}
    corrected = naive_top1_source is not None and naive_top1_source not in used_sources

    if not kept:
        return "I don't have any information relevant to that question.", corrected

    context = "\n\n".join(f"[{c['source']}]\n{refine(effective_query, c['text'])}" for c in kept)
    prompt = f"""Answer the question using only the context below, citing \
the source file in brackets like [source.md]. If the context doesn't \
contain the answer, say so, don't guess.

Context:
{context}

Question: {effective_query}"""
    return call_model(prompt), corrected


def main() -> None:
    store = build_vector_store()
    print(f"Loaded and embedded {len(store)} notes from {NOTES_DIR}\n")

    questions = [
        "Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?",
        "What's the cold ferment time for the pizza dough?",
    ]

    for question in questions:
        answer, corrected = ask(question, store)
        indicator = "[retrieval was corrected]" if corrected else "[no correction needed]"
        print(f"Q: {question}")
        print(f"  {indicator}")
        print(f"A: {answer}\n")


if __name__ == "__main__":
    main()
