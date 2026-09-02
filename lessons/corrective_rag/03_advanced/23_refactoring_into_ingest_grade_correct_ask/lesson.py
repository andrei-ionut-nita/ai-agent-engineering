"""
Lesson 23: refactoring into ingest() and ask(), the series' shared
Strategy shape (see docs/RAG-SERIES-PLAN/README.md), with grade() and
correct() as the internal steps ask() calls. State = (chroma_collection,
grader).

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/03_advanced/23_refactoring_into_ingest_grade_correct_ask/lesson.py
"""

import time
from dataclasses import dataclass
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"

GRADE_PROMPT = """You are grading whether a retrieved passage is relevant \
enough to help answer a question. Respond with exactly one word: \
"relevant" or "not_relevant".

Question: {question}

Passage:
{passage}"""

REWRITE_PROMPT = """The question below was just asked against a small \
notes collection, and none of the retrieved passages were relevant. \
Rewrite the question to be clearer or more specific. Reply with only \
the rewritten question.

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


@dataclass
class Grader:
    # The retrieval evaluator (Lessons 3, 12), packaged as an object so
    # it can live inside this course's State alongside the chromadb
    # collection, instead of being a bare module-level function. Nothing
    # about its grading logic changes here, only where it lives.
    model: str = CHAT_MODEL

    def grade(self, question: str, passage: str) -> str:
        prompt = GRADE_PROMPT.format(question=question, passage=passage)
        grade = call_model(prompt).strip().lower()
        return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


@dataclass
class CorrectiveState:
    # This course's State from the series' shared Strategy protocol
    # (docs/RAG-SERIES-PLAN/README.md): everything ask() needs to answer
    # a question, built once by ingest(). A chromadb collection for
    # retrieval, and a Grader for correction, nothing else.
    collection: chromadb.Collection
    grader: Grader


def ingest(notes_dir: Path) -> CorrectiveState:
    paths = sorted(notes_dir.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)

    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="notes")
    collection.add(
        ids=[path.stem for path in paths],
        documents=texts,
        embeddings=vectors,
        metadatas=[{"source": path.name} for path in paths],
    )
    return CorrectiveState(collection=collection, grader=Grader())


def _retrieve(query: str, collection: chromadb.Collection, k: int) -> list[dict]:
    query_vector = embed_texts([query])[0]
    results = collection.query(query_embeddings=[query_vector], n_results=k)
    documents = results["documents"]
    metadatas = results["metadatas"]
    assert documents is not None and metadatas is not None
    return [
        {"text": doc, "source": meta["source"]}
        for doc, meta in zip(documents[0], metadatas[0])
    ]


def grade(query: str, chunks: list[dict], grader: Grader) -> list[dict]:
    return [{**c, "grade": grader.grade(query, c["text"])} for c in chunks]


def correct(query: str, graded_chunks: list[dict], state: CorrectiveState, k: int) -> tuple[str, list[dict]]:
    relevant = [c for c in graded_chunks if c["grade"] == "relevant"]
    if relevant:
        return query, relevant

    rewritten = call_model(REWRITE_PROMPT.format(question=query)).strip()
    retrieved = _retrieve(rewritten, state.collection, k)
    re_graded = grade(rewritten, retrieved, state.grader)
    return rewritten, [c for c in re_graded if c["grade"] == "relevant"]


def ask(query: str, state: CorrectiveState, k: int = 2) -> str:
    # The Strategy protocol's ask(): retrieve, grade, correct if needed,
    # generate. Everything here is Lessons 2-9's pipeline, unchanged,
    # now expressed through grade() and correct() as named steps instead
    # of inline code.
    retrieved = _retrieve(query, state.collection, k)
    graded = grade(query, retrieved, state.grader)
    effective_query, relevant = correct(query, graded, state, k)

    if not relevant:
        return "I don't have any information relevant to that question."

    context = "\n\n---\n\n".join(c["text"] for c in relevant)
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {effective_query}"""
    return call_model(prompt)


def main() -> None:
    notes_dir = Path(__file__).parent.parent.parent / "fixtures" / "notes"
    state = ingest(notes_dir)
    print(f"Ingested {state.collection.count()} documents into chromadb\n")

    for query in (
        "Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?",
        "What is the capital of France?",
    ):
        print(f"Q: {query}")
        print(f"A: {ask(query, state)}\n")


if __name__ == "__main__":
    main()
