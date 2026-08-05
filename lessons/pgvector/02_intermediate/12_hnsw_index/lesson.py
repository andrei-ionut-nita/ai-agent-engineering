"""
Lesson 12: hnsw, pgvector's graph-based ANN index.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/02_intermediate/12_hnsw_index/lesson.py
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
SEED = 42  # Same seed as Lessons 10-11: the identical synthetic dataset.


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

        # m=16, ef_construction=64 are pgvector's own defaults, a
        # reasonable starting point before tuning for a specific dataset.
        t0 = time.perf_counter()
        conn.execute(
            "CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops) "
            "WITH (m = 16, ef_construction = 64)"
        )
        build_time = time.perf_counter() - t0
        print(f"Index build time: {build_time:.2f} s")
        print("(compare to ivfflat's build time in Lesson 11, HNSW builds are slower)\n")

        for ef_search in (10, 100):
            conn.execute(f"SET hnsw.ef_search = {ef_search}")
            t0 = time.perf_counter()
            results = conn.execute(
                "SELECT id FROM items ORDER BY embedding <=> %s LIMIT 10",
                (query_vector,),
            ).fetchall()
            elapsed = time.perf_counter() - t0
            print(
                f"ef_search={ef_search:<4} query time: {elapsed * 1000:.2f} ms  "
                f"ids: {[r[0] for r in results]}"
            )

        print(
            "\nCompare to Lesson 10's brute-force result "
            "([9193, 6034, 5427, 4697, 3637, 4052, ...]) and Lesson 11's "
            "ivfflat result at probes=50: HNSW gets noticeably closer to "
            "the exact answer here, even at a low ef_search, and stays "
            "fast at a high one, on the very same worst-case random data."
        )


if __name__ == "__main__":
    main()
