"""
Lesson 25: halfvec, trading precision for half the storage, measured
against a real ranking comparison, not just asserted.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/03_advanced/25_quantization_and_halfvec/lesson.py
"""

import os

import numpy as np
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from pgvector.utils import HalfVector, Vector

load_dotenv()

DIMENSIONS = 768
ROW_COUNT = 2_000
SEED = 11


def main() -> None:
    rng = np.random.default_rng(SEED)
    vectors = rng.normal(size=(ROW_COUNT, DIMENSIONS)).astype("float32")
    query_vector = rng.normal(size=DIMENSIONS).astype("float32")

    dsn = os.environ["POSTGRES_DSN"]
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)

        conn.execute("DROP TABLE IF EXISTS quant_items")
        conn.execute(
            f"""
            CREATE TABLE quant_items (
                id bigserial PRIMARY KEY,
                embedding vector({DIMENSIONS}),
                embedding_half halfvec({DIMENSIONS})
            )
            """
        )
        with conn.cursor() as cur, cur.copy(
            "COPY quant_items (embedding, embedding_half) FROM STDIN"
        ) as copy:
            for vector in vectors:
                copy.write_row((Vector(vector), HalfVector(vector)))

        sizes = conn.execute(
            "SELECT pg_column_size(embedding), pg_column_size(embedding_half) "
            "FROM quant_items LIMIT 1"
        ).fetchone()
        full_bytes, half_bytes = sizes
        print(f"Per-row storage: vector={full_bytes} bytes, halfvec={half_bytes} bytes")
        print(f"({full_bytes / half_bytes:.1f}x smaller)\n")

        full_results = conn.execute(
            "SELECT id FROM quant_items ORDER BY embedding <=> %s LIMIT 5",
            (Vector(query_vector),),
        ).fetchall()
        half_results = conn.execute(
            "SELECT id FROM quant_items ORDER BY embedding_half <=> %s LIMIT 5",
            (HalfVector(query_vector),),
        ).fetchall()

        full_ids = [row[0] for row in full_results]
        half_ids = [row[0] for row in half_results]
        print(f"Top-5 nearest neighbors, full precision:  {full_ids}")
        print(f"Top-5 nearest neighbors, half precision:  {half_ids}")
        matches = len(set(full_ids) & set(half_ids))
        print(f"\n{matches} of 5 match exactly, at half the storage cost.")


if __name__ == "__main__":
    main()
