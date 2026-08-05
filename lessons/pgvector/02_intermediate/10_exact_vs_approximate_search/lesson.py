"""
Lesson 10: exact search versus approximate nearest neighbor, on a
larger synthetic dataset where "check every row" stops being free.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/02_intermediate/10_exact_vs_approximate_search/lesson.py
"""

import os
import time

import numpy as np
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from pgvector.utils import Vector

load_dotenv()

DIMENSIONS = 768
ROW_COUNT = 10_000
# A fixed seed so every lesson in this tier generates the identical
# synthetic dataset, real meaning doesn't matter here, only scale does.
SEED = 42


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

        # COPY streams rows in one pass, much faster than executemany
        # for bulk loads like this (Lesson 15 covers why).
        with conn.cursor() as cur, cur.copy("COPY items (embedding) FROM STDIN") as copy:
            for vector in vectors:
                copy.write_row((Vector(vector),))

        print(f"Loaded {ROW_COUNT} rows, {DIMENSIONS} dimensions each, no index yet.\n")

        # No index exists: this MUST check every row to guarantee the
        # true closest 10, a sequential scan.
        t0 = time.perf_counter()
        results = conn.execute(
            "SELECT id FROM items ORDER BY embedding <=> %s LIMIT 10",
            (query_vector,),
        ).fetchall()
        elapsed = time.perf_counter() - t0

        print(f"Brute-force (sequential scan) top-10 search: {elapsed * 1000:.2f} ms")
        print(f"Result ids: {[row[0] for row in results]}")
        print(
            "\nThis result is exactly correct, by construction, every row was "
            "checked. Lesson 11 adds an index to this same query and times "
            "the difference."
        )


if __name__ == "__main__":
    main()
