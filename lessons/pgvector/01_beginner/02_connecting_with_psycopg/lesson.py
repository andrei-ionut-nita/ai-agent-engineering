"""
Lesson 2: connecting with psycopg, cursors, and parameterized SQL.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/01_beginner/02_connecting_with_psycopg/lesson.py
"""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    dsn = os.environ["POSTGRES_DSN"]

    with psycopg.connect(dsn, autocommit=True) as conn:
        # A cursor is the object that actually sends a query and holds
        # its results.
        with conn.cursor() as cur:
            cur.execute("SELECT 1 + 1")
            result = cur.fetchone()
            print(f"SELECT 1 + 1  ->  {result[0]}")

        # %s placeholders are filled in safely by psycopg, never build
        # SQL by f-string-ing values in directly (SQL injection risk).
        with conn.cursor() as cur:
            cur.execute("SELECT %s + %s", (2, 3))
            result = cur.fetchone()
            print(f"SELECT %s + %s  ->  {result[0]}")

        # conn.execute(...) is a shortcut: it creates a cursor for you
        # and returns it, handy for one-off queries like Lesson 1's.
        rows = conn.execute(
            "SELECT * FROM (VALUES ('a', 1), ('b', 2), ('c', 3)) AS t(letter, number)"
        ).fetchall()
        print(f"fetchall() on a multi-row query  ->  {rows}")


if __name__ == "__main__":
    main()
