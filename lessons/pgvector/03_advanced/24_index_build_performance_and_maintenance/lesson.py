"""
Lesson 24: maintenance_work_mem, CONCURRENTLY, and when ivfflat needs a
full REINDEX after bulk data growth.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/03_advanced/24_index_build_performance_and_maintenance/lesson.py

This lesson's index builds take a while (tens of seconds total), that's
the point, it's timing real build cost.
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
ROW_COUNT = 20_000
SEED = 9


def main() -> None:
    rng = np.random.default_rng(SEED)
    vectors = rng.normal(size=(ROW_COUNT, DIMENSIONS)).astype("float32")

    dsn = os.environ["POSTGRES_DSN"]
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)

        conn.execute("DROP TABLE IF EXISTS maint_items")
        conn.execute(
            f"CREATE TABLE maint_items (id bigserial PRIMARY KEY, embedding vector({DIMENSIONS}))"
        )
        with conn.cursor() as cur, cur.copy("COPY maint_items (embedding) FROM STDIN") as copy:
            for vector in vectors:
                copy.write_row((Vector(vector),))

        print(f"Loaded {ROW_COUNT} rows. Timing the same hnsw build at two memory settings:\n")

        for mem in ("64MB", "512MB"):
            conn.execute(f"SET maintenance_work_mem = '{mem}'")
            conn.execute("DROP INDEX IF EXISTS maint_items_embedding_idx")
            t0 = time.perf_counter()
            conn.execute("CREATE INDEX ON maint_items USING hnsw (embedding vector_cosine_ops)")
            elapsed = time.perf_counter() - t0
            print(f"  maintenance_work_mem = {mem:<7} build time: {elapsed:.2f} s")

        conn.execute("DROP INDEX IF EXISTS maint_items_embedding_idx")

        print("\nBuilding the same index again with CONCURRENTLY (no write lock this time):\n")
        t0 = time.perf_counter()
        conn.execute(
            "CREATE INDEX CONCURRENTLY ON maint_items USING hnsw (embedding vector_cosine_ops)"
        )
        elapsed = time.perf_counter() - t0
        print(f"  CREATE INDEX CONCURRENTLY build time: {elapsed:.2f} s")
        print(
            "\nThis is the version to use against a table a live application "
            "is still writing to, plain CREATE INDEX would block those writes "
            "for the entire build."
        )


if __name__ == "__main__":
    main()
