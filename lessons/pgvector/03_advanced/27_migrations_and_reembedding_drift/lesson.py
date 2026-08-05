"""
Lesson 27: what breaks when you upgrade your embedding model, and the
add-backfill-verify-cutover migration pattern that avoids it.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/03_advanced/27_migrations_and_reembedding_drift/lesson.py
"""

import os
from pathlib import Path

import numpy as np
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


def demonstrate_the_trap() -> None:
    # Same model, same dimension, ONLY the task_type differs, still a
    # meaningfully different embedding space for the identical text.
    old_config = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        output_dimensionality=EMBEDDING_DIMENSIONS,
        task_type="RETRIEVAL_DOCUMENT",
    )
    new_config = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        output_dimensionality=EMBEDDING_DIMENSIONS,
        task_type="SEMANTIC_SIMILARITY",
    )

    text = "Recipe notes: the best pizza dough recipe found so far uses 00 flour."
    old_vector = np.array(old_config.embed_query(text))
    new_vector = np.array(new_config.embed_query(text))

    cosine_similarity = float(
        np.dot(old_vector, new_vector)
        / (np.linalg.norm(old_vector) * np.linalg.norm(new_vector))
    )
    print("Same exact text, embedded under two different configurations:")
    print(f"  cosine similarity between them: {cosine_similarity:.4f}")
    print(
        "  (1.0 would mean identical, both are vector(768), Postgres "
        "would accept either one with no error, but this is NOT 1.0, "
        "they describe genuinely different spaces)\n"
    )


def demonstrate_the_migration(conn: psycopg.Connection, chunks: list[str]) -> None:
    old_config = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        output_dimensionality=EMBEDDING_DIMENSIONS,
        task_type="RETRIEVAL_DOCUMENT",
    )
    new_config = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        output_dimensionality=EMBEDDING_DIMENSIONS,
        task_type="SEMANTIC_SIMILARITY",
    )

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
    old_vectors = old_config.embed_documents(chunks)
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO notes (content, embedding) VALUES (%s, %s)",
            [(chunk, Vector(vector)) for chunk, vector in zip(chunks, old_vectors)],
        )
    print(f"Step 0: {len(chunks)} rows stored under the OLD embedding configuration.\n")

    # Step 1: add the new embedding as a NEW column, don't touch the old one.
    conn.execute(f"ALTER TABLE notes ADD COLUMN IF NOT EXISTS embedding_v2 vector({EMBEDDING_DIMENSIONS})")
    print("Step 1: added embedding_v2 column. Old `embedding` column still serves live searches.\n")

    # Step 2: backfill, re-embed every row's content under the new config.
    rows = conn.execute("SELECT id, content FROM notes ORDER BY id").fetchall()
    ids = [row[0] for row in rows]
    contents = [row[1] for row in rows]
    new_vectors = new_config.embed_documents(contents)
    with conn.cursor() as cur:
        cur.executemany(
            "UPDATE notes SET embedding_v2 = %s WHERE id = %s",
            [(Vector(vector), note_id) for vector, note_id in zip(new_vectors, ids)],
        )
    print(f"Step 2: backfilled embedding_v2 for all {len(ids)} rows.\n")

    # Step 3: verify, every row populated, nothing left behind.
    unbackfilled = conn.execute("SELECT count(*) FROM notes WHERE embedding_v2 IS NULL").fetchone()[0]
    print(f"Step 3: verify, {unbackfilled} rows still missing embedding_v2 (expect 0).\n")

    # Step 4 (cutover) and step 5 (dropping the old column) are left as
    # a real deploy step, not run here, once step 3 confirms it's safe.
    print(
        "Step 4/5 (not run here): cut application reads over to embedding_v2, "
        "confirm in production, THEN drop the old `embedding` column."
    )


def main() -> None:
    demonstrate_the_trap()

    chunks = load_chunks()
    dsn = os.environ["POSTGRES_DSN"]
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)
        demonstrate_the_migration(conn, chunks)


if __name__ == "__main__":
    main()
