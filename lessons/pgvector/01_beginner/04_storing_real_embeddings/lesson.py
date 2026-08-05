"""
Lesson 4: storing real embeddings, from the same notes.txt langchain
Lesson 28 used for InMemoryVectorStore.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/01_beginner/04_storing_real_embeddings/lesson.py
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

# Used everywhere in this course: short enough to stay under pgvector's
# 2000-dimension index limit, long enough to still capture meaning well.
EMBEDDING_DIMENSIONS = 768


def load_chunks() -> list[str]:
    text = NOTES_PATH.read_text()
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    return splitter.split_text(text)


def main() -> None:
    chunks = load_chunks()

    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        output_dimensionality=EMBEDDING_DIMENSIONS,
    )
    # Embeds every chunk in one call, one vector per chunk.
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

        count = conn.execute("SELECT count(*) FROM notes").fetchone()[0]
        print(f"Stored {count} chunks, each with a {EMBEDDING_DIMENSIONS}-dimension embedding.")

        first = conn.execute("SELECT content FROM notes ORDER BY id LIMIT 1").fetchone()
        print(f"\nFirst chunk stored:\n{first[0]}")


if __name__ == "__main__":
    main()
