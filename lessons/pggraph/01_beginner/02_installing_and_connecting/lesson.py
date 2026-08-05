"""
Lesson 2: confirming both Postgres containers, and reading graph.status().

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    docker compose up -d
    uv run python lessons/pggraph/01_beginner/02_installing_and_connecting/lesson.py
"""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    # Two separate containers, two separate DSNs. This lesson connects to
    # both just to make the split concrete, later lessons only use
    # PGGRAPH_DSN.
    with psycopg.connect(os.environ["POSTGRES_DSN"], connect_timeout=3) as conn:
        db = conn.execute("SELECT current_database()").fetchone()[0]
        print(f"pgvector container: database '{db}'")

    with psycopg.connect(os.environ["PGGRAPH_DSN"], connect_timeout=3) as conn:
        db = conn.execute("SELECT current_database()").fetchone()[0]
        print(f"pggraph container: database '{db}'")

        # graph.status() reports on the graph itself, not the underlying
        # Postgres connection. Nothing has been registered yet, so both
        # counts are 0, that's the expected state for a fresh container.
        node_count, edge_count = conn.execute(
            "SELECT node_count, edge_count FROM graph.status()"
        ).fetchone()
        print(f"graph.status(): node_count={node_count}, edge_count={edge_count}")


if __name__ == "__main__":
    main()
