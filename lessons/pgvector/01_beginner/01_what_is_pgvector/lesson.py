"""
Lesson 1: what pgvector is, and turning the extension on.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/01_beginner/01_what_is_pgvector/lesson.py
"""

import os

import psycopg
from dotenv import load_dotenv

# Reads POSTGRES_DSN from the project root's .env, the same way every
# other course reads GOOGLE_API_KEY.
load_dotenv()


def main() -> None:
    dsn = os.environ["POSTGRES_DSN"]

    # A plain Postgres connection, nothing pgvector-specific yet.
    with psycopg.connect(dsn, autocommit=True) as conn:
        # Enables the vector column type for this database. Safe to run
        # every time: a no-op if a previous run already did it.
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

        # Prove it worked by asking Postgres's own catalog, not just
        # trusting that the CREATE EXTENSION line didn't error.
        row = conn.execute(
            "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'"
        ).fetchone()

        server_version = conn.execute("SHOW server_version").fetchone()

    name, version = row
    print(f"Connected to Postgres {server_version[0]}")
    print(f"Extension '{name}' is enabled, version {version}")


if __name__ == "__main__":
    main()
