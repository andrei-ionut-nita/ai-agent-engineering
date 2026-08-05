"""
Lesson 5: the three distance operators, <->, <#>, <=>.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/01_beginner/05_distance_operators/lesson.py
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

        # Embed a query with no exact word overlap with any chunk, the
        # same trick langchain Lesson 28 used, to show this is matching
        # on MEANING, not keywords.
        query = "What do I know about baking bread at home?"
        query_vector = Vector(embeddings_model.embed_query(query))

        print(f"Query: {query}\n")

        for label, operator in [
            ("L2 distance          (<->)", "<->"),
            ("negative inner product (<#>)", "<#>"),
            ("cosine distance       (<=>)", "<=>"),
        ]:
            row = conn.execute(
                f"""
                SELECT content, embedding {operator} %s AS distance
                FROM notes
                ORDER BY distance
                LIMIT 1
                """,
                (query_vector,),
            ).fetchone()
            content, distance = row
            print(f"{label}: distance={distance:.4f}")
            print(f"  closest chunk: {content.splitlines()[0]}...\n")


if __name__ == "__main__":
    main()
