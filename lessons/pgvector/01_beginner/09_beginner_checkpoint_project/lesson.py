"""
Lesson 9: Beginner Checkpoint - Notes Semantic Search CLI.

No new concepts, this combines Lessons 1-8 into one small script.
Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/01_beginner/09_beginner_checkpoint_project/lesson.py
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
CATEGORIES = ["project", "garden", "garden", "recipe", "household", "hobby"]


def load_chunks() -> list[str]:
    text = NOTES_PATH.read_text()
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    return splitter.split_text(text)


def search(conn, embeddings_model, query: str, k: int, category: str | None = None):
    query_vector = Vector(embeddings_model.embed_query(query))
    if category is None:
        return conn.execute(
            "SELECT content, embedding <=> %s AS distance FROM notes ORDER BY distance LIMIT %s",
            (query_vector, k),
        ).fetchall()
    return conn.execute(
        """
        SELECT content, embedding <=> %s AS distance
        FROM notes
        WHERE category = %s
        ORDER BY distance
        LIMIT %s
        """,
        (query_vector, category, k),
    ).fetchall()


def print_results(title: str, results: list[tuple[str, float]]) -> None:
    print(f"--- {title} ---")
    for content, distance in results:
        print(f"  (distance={distance:.4f}) {content.splitlines()[0]}...")
    print()


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

        print_results(
            "Plain search: 'What do I know about baking bread at home?'",
            search(conn, embeddings_model, "What do I know about baking bread at home?", k=2),
        )

        print_results(
            "Category-filtered search (category='garden'): 'what's planted together?'",
            search(conn, embeddings_model, "what's planted together?", k=1, category="garden"),
        )

        # Edit a note, then re-embed it, the Lesson 8 lifecycle.
        recipe_id = conn.execute(
            "SELECT id FROM notes WHERE content LIKE 'Recipe notes%'"
        ).fetchone()[0]
        new_content = "Recipe notes: switched entirely to sourdough starter, no commercial yeast."
        new_vector = Vector(embeddings_model.embed_query(new_content))
        conn.execute(
            "UPDATE notes SET content = %s, embedding = %s WHERE id = %s",
            (new_content, new_vector, recipe_id),
        )

        print_results(
            "Same bread query, after the recipe note was edited to remove yeast",
            search(conn, embeddings_model, "flour and yeast for baking", k=1),
        )


if __name__ == "__main__":
    main()
