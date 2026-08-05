"""
Lesson 28: Advanced Capstone - A FastAPI RAG Service on pgvector.

No new pgvector concepts, this wires Lessons 1-27 into one small web
service. Read README.md in this folder first, then read this file top
to bottom, then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/03_advanced/28_advanced_capstone_project/lesson.py

To run this as a real, live server instead:

    uvicorn lesson:app --reload
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pgvector.psycopg import register_vector
from pgvector.utils import Vector
from psycopg_pool import ConnectionPool
from pydantic import BaseModel

load_dotenv()

NOTES_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "langchain"
    / "03_advanced"
    / "27_document_loading_and_splitting"
    / "data"
    / "notes.txt"
)
EMBEDDING_DIMENSIONS = 768
CATEGORIES = ["project", "garden", "garden", "recipe", "household", "hobby"]


def reciprocal_rank_fusion(*rankings: list[str], k: int = 60) -> dict[str, float]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1 / (k + rank)
    return scores


class NoteIn(BaseModel):
    external_id: str
    content: str
    category: str


class SearchResult(BaseModel):
    content: str
    score: float


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    dsn_raw = os.environ["POSTGRES_DSN"]
    dsn_sqlalchemy = dsn_raw.replace("postgresql://", "postgresql+psycopg://")

    # Extension must exist before the pool's connections call
    # register_vector (Lesson 19's bootstrap-then-pool ordering).
    with psycopg.connect(dsn_raw, autocommit=True) as bootstrap_conn:
        bootstrap_conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        bootstrap_conn.execute("DROP TABLE IF EXISTS notes")
        bootstrap_conn.execute(
            f"""
            CREATE TABLE notes (
                external_id text PRIMARY KEY,
                content text NOT NULL,
                category text NOT NULL,
                embedding vector({EMBEDDING_DIMENSIONS}),
                content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
            )
            """
        )

    app.state.pool = ConnectionPool(
        conninfo=dsn_raw, min_size=2, max_size=10, configure=register_vector
    )
    app.state.pool.wait()

    app.state.embeddings_model = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        output_dimensionality=EMBEDDING_DIMENSIONS,
    )
    app.state.vector_store = PGVector(
        embeddings=app.state.embeddings_model,
        connection=dsn_sqlalchemy,
        collection_name="capstone_notes",
        pre_delete_collection=True,
    )
    app.state.chat_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

    yield

    app.state.pool.close()


app = FastAPI(lifespan=lifespan)


@app.post("/notes")
def upsert_notes(notes: list[NoteIn]) -> dict:
    vectors = app.state.embeddings_model.embed_documents([note.content for note in notes])
    with app.state.pool.connection() as conn, conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO notes (external_id, content, category, embedding)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (external_id) DO UPDATE
            SET content = EXCLUDED.content,
                category = EXCLUDED.category,
                embedding = EXCLUDED.embedding
            """,
            [
                (note.external_id, note.content, note.category, Vector(vector))
                for note, vector in zip(notes, vectors)
            ],
        )
        conn.execute("CREATE INDEX IF NOT EXISTS notes_embedding_idx ON notes USING hnsw (embedding vector_cosine_ops)")
    # Keep PGVector's own collection in sync too, so /ask can retrieve
    # through the langchain-compatible store from Lesson 20-21.
    app.state.vector_store.add_texts(
        [note.content for note in notes],
        ids=[note.external_id for note in notes],
    )
    return {"upserted": len(notes)}


@app.get("/search", response_model=list[SearchResult])
def hybrid_search(q: str, k: int = 3) -> list[SearchResult]:
    query_vector = Vector(app.state.embeddings_model.embed_query(q))
    with app.state.pool.connection() as conn:
        vector_ranking = [
            row[0]
            for row in conn.execute(
                "SELECT external_id FROM notes ORDER BY embedding <=> %s LIMIT 6",
                (query_vector,),
            ).fetchall()
        ]
        text_ranking = [
            row[0]
            for row in conn.execute(
                """
                SELECT external_id FROM notes
                ORDER BY ts_rank(content_tsv, plainto_tsquery('english', %s)) DESC
                LIMIT 6
                """,
                (q,),
            ).fetchall()
        ]
        content_by_id = dict(conn.execute("SELECT external_id, content FROM notes").fetchall())

    fused = reciprocal_rank_fusion(vector_ranking, text_ranking)
    ranked = sorted(fused.items(), key=lambda item: item[1], reverse=True)[:k]
    return [SearchResult(content=content_by_id[doc_id], score=score) for doc_id, score in ranked]


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    retriever = app.state.vector_store.as_retriever(search_kwargs={"k": 2})
    prompt = ChatPromptTemplate.from_template(
        "Answer the question using only the context below.\n\n"
        "Context:\n{context}\n\nQuestion: {question}"
    )

    def format_docs(docs) -> str:
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | app.state.chat_model
        | StrOutputParser()
    )
    return AskResponse(answer=chain.invoke(request.question))


def load_chunks() -> list[str]:
    text = NOTES_PATH.read_text()
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    return splitter.split_text(text)


def main() -> None:
    chunks = load_chunks()
    notes = [
        {"external_id": f"note-{i}", "content": chunk, "category": category}
        for i, (chunk, category) in enumerate(zip(chunks, CATEGORIES))
    ]

    with TestClient(app) as client:
        response = client.post("/notes", json=notes)
        print(f"POST /notes -> {response.json()}\n")

        response = client.get("/search", params={"q": "yeast", "k": 3})
        print("GET /search?q=yeast:")
        for result in response.json():
            print(f"  score={result['score']:.4f}  {result['content'].splitlines()[0]}...")
        print()

        question = "What do I know about baking bread at home?"
        response = client.post("/ask", json={"question": question})
        print(f"POST /ask: {question}")
        print(f"  answer: {response.json()['answer']}")


if __name__ == "__main__":
    main()
