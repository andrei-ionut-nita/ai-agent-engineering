"""
Lesson 14: reading EXPLAIN ANALYZE, confirming an index is actually used.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/02_intermediate/14_explain_analyze_for_vector_queries/lesson.py
"""

import os

import numpy as np
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from pgvector.utils import Vector

load_dotenv()

DIMENSIONS = 768
ROW_COUNT = 10_000
SEED = 42  # Same seed as Lessons 10-12: the identical synthetic dataset.


def print_plan(conn: psycopg.Connection, query_vector: Vector) -> None:
    rows = conn.execute(
        "EXPLAIN (ANALYZE, COSTS OFF) "
        "SELECT id FROM items ORDER BY embedding <=> %s LIMIT 10",
        (query_vector,),
    ).fetchall()
    for (line,) in rows:
        # The plan embeds the full query vector literal on some lines;
        # truncated here only for readable console output.
        print(f"  {line[:100]}{'...' if len(line) > 100 else ''}")


def main() -> None:
    rng = np.random.default_rng(SEED)
    vectors = rng.normal(size=(ROW_COUNT, DIMENSIONS)).astype("float32")
    query_vector = Vector(rng.normal(size=DIMENSIONS).astype("float32"))

    dsn = os.environ["POSTGRES_DSN"]
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)

        conn.execute("DROP TABLE IF EXISTS items")
        conn.execute(f"CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector({DIMENSIONS}))")
        with conn.cursor() as cur, cur.copy("COPY items (embedding) FROM STDIN") as copy:
            for vector in vectors:
                copy.write_row((Vector(vector),))

        print("Plan with NO index (expect Seq Scan):\n")
        print_plan(conn, query_vector)

        conn.execute("CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops)")

        print("\nPlan with an hnsw index built (expect Index Scan, no separate Sort):\n")
        print_plan(conn, query_vector)


if __name__ == "__main__":
    main()
