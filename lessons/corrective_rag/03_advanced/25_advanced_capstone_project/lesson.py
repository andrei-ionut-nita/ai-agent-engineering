"""
Lesson 25: Advanced Capstone - A Complete Corrective RAG Service.

No new concepts, this combines Lessons 19-24 into one small web service.
Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/03_advanced/25_advanced_capstone_project/lesson.py

To run this as a real, live server instead:

    uvicorn lesson:app --reload
"""

import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from pydantic import BaseModel

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

PRE_FILTER_MIN_SCORE = 0.55  # Lesson 20
MAX_REWRITE_ATTEMPTS = 1  # Lesson 21, kept small to bound API calls per request

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

# Lesson 22's pluggable external-search fallback, mocked so this
# capstone (like every lesson in this course) needs only GOOGLE_API_KEY.
_MOCK_WEB_INDEX = {"capital of france": "Paris is the capital and most populous city of France."}


def mock_web_search(query: str) -> str | None:
    query_lower = query.lower()
    for keyword, result in _MOCK_WEB_INDEX.items():
        if keyword in query_lower:
            return result
    return None


ExternalSearch = Callable[[str], "str | None"]


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
    def grade(self, question: str, passage: str) -> str:
        grade = call_model(GRADE_PROMPT.format(question=question, passage=passage)).strip().lower()
        return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


@dataclass
class CorrectiveState:
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


def _retrieve_with_scores(query: str, collection: chromadb.Collection, k: int) -> list[dict]:
    query_vector = embed_texts([query])[0]
    results = collection.query(
        query_embeddings=[query_vector], n_results=k, include=["documents", "distances", "metadatas"]
    )
    documents = results["documents"]
    distances = results["distances"]
    metadatas = results["metadatas"]
    assert documents is not None and distances is not None and metadatas is not None
    return [
        {"text": doc, "source": meta["source"], "score": 1 - dist}
        for doc, dist, meta in zip(documents[0], distances[0], metadatas[0])
    ]


def _grade_and_filter(query: str, chunks: list[dict], grader: Grader) -> list[dict]:
    # Lesson 20's pre-filter runs first, cheaply, before spending any
    # grading calls; only what clears it gets a real LLM grade.
    candidates = [c for c in chunks if c["score"] >= PRE_FILTER_MIN_SCORE]
    graded = [{**c, "grade": grader.grade(query, c["text"])} for c in candidates]
    return [c for c in graded if c["grade"] == "relevant"]


def ask(query: str, state: CorrectiveState, k: int = 3, external_search: ExternalSearch = mock_web_search) -> str:
    retrieved = _retrieve_with_scores(query, state.collection, k)
    relevant = _grade_and_filter(query, retrieved, state.grader)

    effective_query = query
    attempts = 0
    while not relevant and attempts < MAX_REWRITE_ATTEMPTS:
        effective_query = call_model(REWRITE_PROMPT.format(question=effective_query)).strip()
        retrieved = _retrieve_with_scores(effective_query, state.collection, k)
        relevant = _grade_and_filter(effective_query, retrieved, state.grader)
        attempts += 1

    if relevant:
        context = "\n\n".join(f"[{c['source']}]\n{c['text']}" for c in relevant)
        source_note = "the notes collection"
    else:
        # Lesson 22's real "incorrect" branch: bounded internal rewriting
        # (Lesson 21) gave up, so fall back to external search instead of
        # rewriting indefinitely against the same corpus.
        web_result = external_search(query)
        if web_result is None:
            return "I don't have any information relevant to that question, internally or externally."
        context = f"[external web search]\n{web_result}"
        source_note = "external web search"

    prompt = f"""Answer the question using only the context below, citing \
the source in brackets like [source.md] or [external web search]. \
Mention that this context came from {source_note} only if it's not \
already obvious from the citation.

Context:
{context}

Question: {effective_query}"""
    return call_model(prompt)


class AskResponse(BaseModel):
    answer: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.corrective_state = ingest(NOTES_DIR)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str, k: int = 3) -> AskResponse:
    return AskResponse(answer=ask(q, app.state.corrective_state, k))


def main() -> None:
    with TestClient(app) as test_client:
        for question in (
            "Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?",
            "What is the capital of France?",
        ):
            response = test_client.get("/ask", params={"q": question})
            print(f"GET /ask?q={question!r}")
            print(f"  {response.json()}\n")


if __name__ == "__main__":
    main()
