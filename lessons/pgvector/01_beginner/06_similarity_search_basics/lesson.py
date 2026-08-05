"""
Lesson 6: ORDER BY ... LIMIT k, the whole top-k search in one query.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/01_beginner/06_similarity_search_basics/lesson.py
"""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pgvector.psycopg import register_vector
from pgvector.utils import Vector

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


def load_chunks() -> list[str]:
    text = NOTES_PATH.read_text()
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    return splitter.split_text(text)


def search(conn: psycopg.Connection, query_vector: Vector, k: int) -> list[tuple[str, float]]:
    return conn.execute(
        """
        SELECT content, embedding <=> %s AS distance
        FROM notes
        ORDER BY distance
        LIMIT %s
        """,
        (query_vector, k),
    ).fetchall()


def main() -> None:
    chunks = load_chunks()
    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        output_dimensionality=EMBEDDING_DIMENSIONS,
    )
    vectors = embeddings_model.embed_documents(chunks)

    dsn = os.environ["POSTGRES_DSN"]
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)

        conn.execute("DROP TABLE IF EXISTS notes")
        conn.execute(
            f"""
            CREATE TABLE notes (
                id bigserial PRIMARY KEY,
                content text NOT NULL,
                embedding vector({EMBEDDING_DIMENSIONS})
            )
            """
        )
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO notes (content, embedding) VALUES (%s, %s)",
                [(chunk, Vector(vector)) for chunk, vector in zip(chunks, vectors)],
            )

        query = "What do I know about baking bread at home?"
        query_vector = Vector(embeddings_model.embed_query(query))

        results = search(conn, query_vector, k=2)

        print(f"Query: {query}\n")
        print(f"Top {len(results)} closest chunks:\n")
        for i, (content, distance) in enumerate(results, start=1):
            print(f"--- Match {i} (distance={distance:.4f}) ---")
            print(content)
            print()


if __name__ == "__main__":
    main()
