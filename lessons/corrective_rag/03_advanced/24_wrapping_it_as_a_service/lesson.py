"""
Lesson 24: wrapping ingest() and ask() as a small FastAPI service,
almost verbatim from naive_rag Lesson 24's pattern.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/03_advanced/24_wrapping_it_as_a_service/lesson.py

To run this as a real, live server instead:

    uvicorn lesson:app --reload
"""

import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

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


def _retrieve(query: str, collection: chromadb.Collection, k: int) -> list[dict]:
    query_vector = embed_texts([query])[0]
    results = collection.query(query_embeddings=[query_vector], n_results=k)
    documents = results["documents"]
    metadatas = results["metadatas"]
    assert documents is not None and metadatas is not None
    return [{"text": doc, "source": meta["source"]} for doc, meta in zip(documents[0], metadatas[0])]


def ask(query: str, state: CorrectiveState, k: int = 2) -> str:
    retrieved = _retrieve(query, state.collection, k)
    graded = [{**c, "grade": state.grader.grade(query, c["text"])} for c in retrieved]
    relevant = [c for c in graded if c["grade"] == "relevant"]

    effective_query = query
    if not relevant:
        effective_query = call_model(REWRITE_PROMPT.format(question=query)).strip()
        retrieved = _retrieve(effective_query, state.collection, k)
        graded = [{**c, "grade": state.grader.grade(effective_query, c["text"])} for c in retrieved]
        relevant = [c for c in graded if c["grade"] == "relevant"]

    if not relevant:
        return "I don't have any information relevant to that question."

    context = "\n\n---\n\n".join(c["text"] for c in relevant)
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {effective_query}"""
    return call_model(prompt)


class AskResponse(BaseModel):
    answer: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ingest() runs once, at startup, exactly Lesson 23's Strategy
    # shape, wired to FastAPI's own startup hook, same as naive_rag
    # Lesson 24.
    app.state.corrective_state = ingest(NOTES_DIR)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str, k: int = 2) -> AskResponse:
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
