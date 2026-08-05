"""
Lesson 1: what pggraph is, and confirming the extension is enabled.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure the pggraph Postgres container is running
first):

    docker compose up -d
    uv run python lessons/pggraph/01_beginner/01_what_is_pggraph/lesson.py
"""

import os

import psycopg
from dotenv import load_dotenv

# Reads PGGRAPH_DSN from the project root's .env, the same way the
# pgvector course reads POSTGRES_DSN. This is a different Postgres
# container (the pggraph image ships its own extension already
# compiled in), so it gets its own DSN.
load_dotenv()


def main() -> None:
    dsn = os.environ["PGGRAPH_DSN"]

    # A plain Postgres connection, nothing pggraph-specific yet. Unlike
    # pgvector, this image ships with the extension already CREATEd in
    # its default "graph" database, there's no CREATE EXTENSION step
    # for you to run, we're just confirming that's true.
    with psycopg.connect(dsn, autocommit=True) as conn:
        server_version = conn.execute("SHOW server_version").fetchone()

        rows = conn.execute(
            "SELECT extname, extversion FROM pg_extension "
            "WHERE extname IN ('graph', 'pg_cron') ORDER BY extname"
        ).fetchall()

    print(f"Connected to Postgres {server_version[0]}")
    for name, version in rows:
        print(f"Extension '{name}' is enabled, version {version}")


if __name__ == "__main__":
    main()
