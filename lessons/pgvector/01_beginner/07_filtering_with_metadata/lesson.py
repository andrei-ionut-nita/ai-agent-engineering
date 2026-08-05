"""
Lesson 7: combining a WHERE filter with vector search.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/01_beginner/07_filtering_with_metadata/lesson.py
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

# Hand-tagged: this is the same six chunks Lesson 6 embedded, each one
# labeled with the topic it actually covers.
CATEGORIES = ["project", "garden", "garden", "recipe", "household", "hobby"]


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
                category text NOT NULL,
                embedding vector({EMBEDDING_DIMENSIONS})
            )
            """
        )
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO notes (content, category, embedding) VALUES (%s, %s, %s)",
                [
                    (chunk, category, Vector(vector))
                    for chunk, category, vector in zip(chunks, CATEGORIES, vectors)
                ],
            )

        # A query that's closest, overall, to the recipe chunk, but
        # we'll ask for the "garden" category instead and see the
        # ranking change to the best match WITHIN that category.
        query = "What do I know about baking bread at home?"
        query_vector = Vector(embeddings_model.embed_query(query))

        print(f"Query: {query}\n")

        unfiltered = conn.execute(
            "SELECT content, embedding <=> %s AS distance FROM notes ORDER BY distance LIMIT 1",
            (query_vector,),
        ).fetchone()
        print(f"Best match overall (distance={unfiltered[1]:.4f}):")
        print(f"  {unfiltered[0].splitlines()[0]}...\n")

        filtered = conn.execute(
            """
            SELECT content, embedding <=> %s AS distance
            FROM notes
            WHERE category = %s
            ORDER BY distance
            LIMIT 1
            """,
            (query_vector, "garden"),
        ).fetchone()
        print(f"Best match within category='garden' (distance={filtered[1]:.4f}):")
        print(f"  {filtered[0].splitlines()[0]}...")


if __name__ == "__main__":
    main()
