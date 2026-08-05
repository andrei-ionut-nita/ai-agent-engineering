"""
Lesson 23: declarative partitioning, structurally solving Lesson 22's
filtered-ANN-search trap via partition pruning.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/03_advanced/23_partitioning_large_tables/lesson.py
"""

import os

import numpy as np
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from pgvector.utils import Vector

load_dotenv()

DIMENSIONS = 256
BIG_TENANT_ROWS = 9_995
SMALL_TENANT_ROWS = 5
SEED = 5  # Same seed as Lesson 22: the identical skewed tenant data.


def main() -> None:
    rng = np.random.default_rng(SEED)
    big_vectors = rng.normal(size=(BIG_TENANT_ROWS, DIMENSIONS)).astype("float32")
    small_vectors = rng.normal(size=(SMALL_TENANT_ROWS, DIMENSIONS)).astype("float32")
    query_vector = Vector(rng.normal(size=DIMENSIONS).astype("float32"))

    dsn = os.environ["POSTGRES_DSN"]
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)

        conn.execute("DROP TABLE IF EXISTS partitioned_items")
        conn.execute(
            f"""
            CREATE TABLE partitioned_items (
                id bigserial,
                tenant_id text NOT NULL,
                embedding vector({DIMENSIONS}),
                PRIMARY KEY (tenant_id, id)
            ) PARTITION BY LIST (tenant_id)
            """
        )
        # Literal partition boundary values, not user input, safe to
        # inline directly into this DDL.
        conn.execute(
            "CREATE TABLE partitioned_items_big PARTITION OF partitioned_items "
            "FOR VALUES IN ('big-tenant')"
        )
        conn.execute(
            "CREATE TABLE partitioned_items_small PARTITION OF partitioned_items "
            "FOR VALUES IN ('small-tenant')"
        )

        with conn.cursor() as cur, cur.copy(
            "COPY partitioned_items (tenant_id, embedding) FROM STDIN"
        ) as copy:
            for vector in big_vectors:
                copy.write_row(("big-tenant", Vector(vector)))
            for vector in small_vectors:
                copy.write_row(("small-tenant", Vector(vector)))

        # One CREATE INDEX statement, but a separate index gets built
        # on EACH partition underneath.
        conn.execute("CREATE INDEX ON partitioned_items USING hnsw (embedding vector_cosine_ops)")

        index_rows = conn.execute(
            "SELECT tablename, indexname FROM pg_indexes "
            "WHERE tablename LIKE 'partitioned_items%' ORDER BY tablename"
        ).fetchall()
        print("Indexes created, one per partition:")
        for table, index in index_rows:
            print(f"  {table}: {index}")

        plan = conn.execute(
            """
            EXPLAIN (ANALYZE, COSTS OFF)
            SELECT id FROM partitioned_items
            WHERE tenant_id = 'small-tenant'
            ORDER BY embedding <=> %s
            LIMIT 5
            """,
            (query_vector,),
        ).fetchall()
        rows = conn.execute(
            """
            SELECT id FROM partitioned_items
            WHERE tenant_id = 'small-tenant'
            ORDER BY embedding <=> %s
            LIMIT 5
            """,
            (query_vector,),
        ).fetchall()

        print("\nQuery plan (notice only the 'small' partition is scanned):")
        for (line,) in plan:
            print(f"  {line[:110]}")

        print(f"\n-> {len(rows)} of {SMALL_TENANT_ROWS} 'small-tenant' rows returned")
        print(
            "Compare to Lesson 22's shared-table result at the default "
            "ef_search: partition pruning means 'big-tenant''s 9,995 rows "
            "are never touched at all, not filtered out after the fact."
        )


if __name__ == "__main__":
    main()
