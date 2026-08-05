"""
Lesson 3: the vector(N) column type, and getting Python lists in and out.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/01_beginner/03_vector_column_and_type/lesson.py
"""

import os

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from pgvector.utils import Vector

load_dotenv()


def main() -> None:
    dsn = os.environ["POSTGRES_DSN"]

    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

        # Teaches THIS connection how to translate Postgres's vector
        # type to and from Python. Without this, inserting a Vector(...)
        # or reading a vector column back would fail.
        register_vector(conn)

        # A fresh table each run, so this lesson is safe to re-run.
        conn.execute("DROP TABLE IF EXISTS items")
        conn.execute(
            """
            CREATE TABLE items (
                id bigserial PRIMARY KEY,
                content text NOT NULL,
                embedding vector(3)
            )
            """
        )

        # Vector([...]) tells psycopg to adapt this list as a `vector`,
        # not as a Postgres array (the default for a plain Python list).
        conn.execute(
            "INSERT INTO items (content, embedding) VALUES (%s, %s)",
            ("first item", Vector([1.0, 2.0, 3.0])),
        )

        row = conn.execute("SELECT content, embedding FROM items WHERE id = 1").fetchone()
        content, embedding = row
        print(f"content: {content}")
        print(f"embedding: {embedding}")
        print(f"type of embedding: {type(embedding)}")

        # vector(3) enforces the dimension: a 4-number vector is rejected.
        try:
            conn.execute(
                "INSERT INTO items (content, embedding) VALUES (%s, %s)",
                ("wrong size", Vector([1.0, 2.0, 3.0, 4.0])),
            )
        except psycopg.errors.DataException as exc:
            print(f"Inserting a 4-dimensional vector into vector(3) failed: {exc}")


if __name__ == "__main__":
    main()
