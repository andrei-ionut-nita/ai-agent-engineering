"""
Lesson 8: keeping stored embeddings in sync with source data.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/01_beginner/08_updating_and_deleting_vectors/lesson.py
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

        recipe_id = conn.execute(
            "SELECT id FROM notes WHERE content LIKE 'Recipe notes%'"
        ).fetchone()[0]

        query = "flour and yeast for baking"
        query_vector = Vector(embeddings_model.embed_query(query))

        before = conn.execute(
            "SELECT content, embedding <=> %s AS distance FROM notes WHERE id = %s",
            (query_vector, recipe_id),
        ).fetchone()
        print(f"Before update, distance to recipe chunk: {before[1]:.4f}")

        # Editing content WITHOUT re-embedding: the query below should
        # NOT be used this way in real code, it's here to show the
        # trap. The embedding now describes text that no longer exists.
        stale_content = "Recipe notes: switched entirely to sourdough starter, no commercial yeast."
        conn.execute("UPDATE notes SET content = %s WHERE id = %s", (stale_content, recipe_id))

        stale = conn.execute(
            "SELECT content, embedding <=> %s AS distance FROM notes WHERE id = %s",
            (query_vector, recipe_id),
        ).fetchone()
        print(f"\nAfter editing content but NOT re-embedding:")
        print(f"  content is now: {stale[0]}")
        print(f"  distance is STILL: {stale[1]:.4f} (unchanged, the embedding is stale)")

        # The fix: re-run the embedding call as part of the same update.
        fresh_vector = Vector(embeddings_model.embed_query(stale_content))
        conn.execute(
            "UPDATE notes SET embedding = %s WHERE id = %s",
            (fresh_vector, recipe_id),
        )

        fresh = conn.execute(
            "SELECT content, embedding <=> %s AS distance FROM notes WHERE id = %s",
            (query_vector, recipe_id),
        ).fetchone()
        print(f"\nAfter re-embedding:")
        print(f"  distance is now: {fresh[1]:.4f} (correctly changed, no more yeast mentioned)")

        conn.execute("DELETE FROM notes WHERE id = %s", (recipe_id,))
        remaining = conn.execute("SELECT count(*) FROM notes").fetchone()[0]
        print(f"\nAfter DELETE, {remaining} rows remain (started with {len(chunks)}).")


if __name__ == "__main__":
    main()
