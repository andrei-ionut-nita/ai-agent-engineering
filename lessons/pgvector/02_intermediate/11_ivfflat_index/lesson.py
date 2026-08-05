"""
Lesson 11: ivfflat, pgvector's clustering-based ANN index.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/02_intermediate/11_ivfflat_index/lesson.py
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
SEED = 42  # Same seed as Lesson 10: the identical synthetic dataset.


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

        # Built AFTER loading the data, ivfflat needs real vectors to
        # cluster. lists=100 follows pgvector's own rule of thumb
        # (rows / 1000) for a table this size.
        t0 = time.perf_counter()
        conn.execute(
            "CREATE INDEX ON items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
        )
        build_time = time.perf_counter() - t0
        print(f"Index build time: {build_time:.2f} s\n")

        for probes in (1, 50):
            conn.execute(f"SET ivfflat.probes = {probes}")
            t0 = time.perf_counter()
            results = conn.execute(
                "SELECT id FROM items ORDER BY embedding <=> %s LIMIT 10",
                (query_vector,),
            ).fetchall()
            elapsed = time.perf_counter() - t0
            print(f"probes={probes:<3} query time: {elapsed * 1000:.2f} ms  ids: {[r[0] for r in results]}")

        print(
            "\nCompare the ids above to Lesson 10's brute-force result "
            "([9193, 6034, 5427, ...]): with probes=1, ivfflat is fast but "
            "misses the true top-10 (low recall). It takes an unusually "
            "high probes value to match exactly here because this dataset "
            "is pure random noise, with no real cluster structure for "
            "ivfflat to exploit. Real embeddings cluster around actual "
            "topics and meanings, so in practice a small number of probes "
            "recovers most of the recall at a fraction of the cost, "
            "exactly the trade Lesson 10 introduced."
        )


if __name__ == "__main__":
    main()
