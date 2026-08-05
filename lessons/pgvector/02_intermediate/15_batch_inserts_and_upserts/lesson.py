"""
Lesson 15: bulk loading, timed honestly, plus upserting with ON CONFLICT.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/02_intermediate/15_batch_inserts_and_upserts/lesson.py
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
SEED = 7


def benchmark_bulk_inserts(conn: psycopg.Connection, vectors: np.ndarray) -> None:
    conn.execute("DROP TABLE IF EXISTS bulk_items")
    conn.execute(f"CREATE TABLE bulk_items (id bigserial PRIMARY KEY, embedding vector({DIMENSIONS}))")

    t0 = time.perf_counter()
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO bulk_items (embedding) VALUES (%s)",
            [(Vector(v),) for v in vectors],
        )
    executemany_time = time.perf_counter() - t0
    print(f"executemany: {executemany_time:.2f} s for {len(vectors)} rows")

    conn.execute("TRUNCATE bulk_items")

    t0 = time.perf_counter()
    with conn.cursor() as cur, cur.copy("COPY bulk_items (embedding) FROM STDIN") as copy:
        for v in vectors:
            copy.write_row((Vector(v),))
    copy_time = time.perf_counter() - t0
    print(f"COPY (row by row): {copy_time:.2f} s for {len(vectors)} rows")

    faster = "executemany" if executemany_time < copy_time else "COPY"
    print(f"\nMeasured faster here: {faster}. Don't trust a rule of thumb, benchmark your own workload.\n")

    conn.execute("DROP TABLE bulk_items")


def demonstrate_upsert(conn: psycopg.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS docs")
    conn.execute(
        "CREATE TABLE docs (external_id text PRIMARY KEY, content text, embedding vector(3))"
    )

    conn.execute(
        "INSERT INTO docs (external_id, content, embedding) VALUES (%s, %s, %s)",
        ("doc-1", "Original content", Vector([1.0, 2.0, 3.0])),
    )
    print("After first insert:", conn.execute("SELECT * FROM docs").fetchall())

    # Re-running "ingestion" over the same external_id: insert-or-update
    # in one statement, no separate SELECT-then-decide needed.
    conn.execute(
        """
        INSERT INTO docs (external_id, content, embedding)
        VALUES (%s, %s, %s)
        ON CONFLICT (external_id) DO UPDATE
        SET content = EXCLUDED.content, embedding = EXCLUDED.embedding
        """,
        ("doc-1", "Updated content", Vector([4.0, 5.0, 6.0])),
    )
    print("After upsert with the same external_id:", conn.execute("SELECT * FROM docs").fetchall())

    conn.execute("DROP TABLE docs")


def main() -> None:
    rng = np.random.default_rng(SEED)
    vectors = rng.normal(size=(ROW_COUNT, DIMENSIONS)).astype("float32")

    dsn = os.environ["POSTGRES_DSN"]
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)

        benchmark_bulk_inserts(conn, vectors)
        demonstrate_upsert(conn)


if __name__ == "__main__":
    main()
