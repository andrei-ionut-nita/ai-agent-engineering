"""
Lesson 16: hybrid search, combining Postgres full-text search with
vector similarity in one query.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/02_intermediate/16_hybrid_search_text_and_vector/lesson.py
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
                embedding vector({EMBEDDING_DIMENSIONS}),
                content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
            )
            """
        )
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO notes (content, embedding) VALUES (%s, %s)",
                [(chunk, Vector(vector)) for chunk, vector in zip(chunks, vectors)],
            )

        # Full-text search alone: exact word matching.
        keyword = "yeast"
        print(f"Full-text search for '{keyword}':")
        rows = conn.execute(
            """
            SELECT content, ts_rank(content_tsv, plainto_tsquery('english', %s)) AS rank
            FROM notes
            WHERE content_tsv @@ plainto_tsquery('english', %s)
            ORDER BY rank DESC
            """,
            (keyword, keyword),
        ).fetchall()
        for content, rank in rows:
            print(f"  rank={rank:.4f}  {content.splitlines()[0]}...")

        # Vector search alone: same query, no exact word overlap needed.
        semantic_query = "fermentation and dough"
        query_vector = Vector(embeddings_model.embed_query(semantic_query))
        print(f"\nVector search for '{semantic_query}':")
        rows = conn.execute(
            "SELECT content, embedding <=> %s AS distance FROM notes ORDER BY distance LIMIT 3",
            (query_vector,),
        ).fetchall()
        for content, distance in rows:
            print(f"  distance={distance:.4f}  {content.splitlines()[0]}...")

        # Hybrid: one weighted score combining both signals.
        hybrid_query = "yeast"
        hybrid_vector = Vector(embeddings_model.embed_query(hybrid_query))
        print(f"\nHybrid search for '{hybrid_query}' (50/50 weighted):")
        rows = conn.execute(
            """
            SELECT
                content,
                (1 - (embedding <=> %s)) * 0.5
                  + ts_rank(content_tsv, plainto_tsquery('english', %s)) * 0.5 AS score
            FROM notes
            ORDER BY score DESC
            LIMIT 3
            """,
            (hybrid_vector, hybrid_query),
        ).fetchall()
        for content, score in rows:
            print(f"  score={score:.4f}  {content.splitlines()[0]}...")


if __name__ == "__main__":
    main()
