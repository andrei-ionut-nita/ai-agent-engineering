"""
Lesson 22: multi-tenant schema design, and the filtered-ANN-search trap,
where a selective WHERE clause on an indexed table can return fewer
rows than truly match, or zero.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/03_advanced/22_schema_design_for_multi_tenant_vectors/lesson.py
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
SEED = 5


def main() -> None:
    rng = np.random.default_rng(SEED)
    big_vectors = rng.normal(size=(BIG_TENANT_ROWS, DIMENSIONS)).astype("float32")
    small_vectors = rng.normal(size=(SMALL_TENANT_ROWS, DIMENSIONS)).astype("float32")
    query_vector = Vector(rng.normal(size=DIMENSIONS).astype("float32"))

    dsn = os.environ["POSTGRES_DSN"]
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)

        conn.execute("DROP TABLE IF EXISTS tenant_items")
        conn.execute(
            f"""
            CREATE TABLE tenant_items (
                id bigserial PRIMARY KEY,
                tenant_id text NOT NULL,
                embedding vector({DIMENSIONS})
            )
            """
        )

        with conn.cursor() as cur, cur.copy(
            "COPY tenant_items (tenant_id, embedding) FROM STDIN"
        ) as copy:
            for vector in big_vectors:
                copy.write_row(("big-tenant", Vector(vector)))
            for vector in small_vectors:
                copy.write_row(("small-tenant", Vector(vector)))

        conn.execute("CREATE INDEX ON tenant_items USING hnsw (embedding vector_cosine_ops)")

        print(
            f"Loaded {BIG_TENANT_ROWS} rows for 'big-tenant' and "
            f"{SMALL_TENANT_ROWS} rows for 'small-tenant', one shared "
            "table, one shared hnsw index.\n"
        )

        for ef_search in (40, 200):
            conn.execute(f"SET hnsw.ef_search = {ef_search}")
            plan = conn.execute(
                """
                EXPLAIN (ANALYZE, COSTS OFF)
                SELECT id FROM tenant_items
                WHERE tenant_id = 'small-tenant'
                ORDER BY embedding <=> %s
                LIMIT 5
                """,
                (query_vector,),
            ).fetchall()
            rows = conn.execute(
                """
                SELECT id FROM tenant_items
                WHERE tenant_id = 'small-tenant'
                ORDER BY embedding <=> %s
                LIMIT 5
                """,
                (query_vector,),
            ).fetchall()

            print(f"ef_search={ef_search}:")
            for (line,) in plan:
                print(f"  {line[:100]}")
            print(f"  -> {len(rows)} of {SMALL_TENANT_ROWS} 'small-tenant' rows returned\n")

        print(
            "Notice which scan type each plan actually used: at the default "
            "ef_search, the Index Scan finds few or none of the 5 rows, "
            "because most (or all) of the graph-walk candidates it checked "
            "belonged to 'big-tenant' instead. At a higher ef_search, "
            "Postgres's planner may switch to a plain Seq Scan instead, "
            "guaranteed correct, once the ANN path's estimated cost stops "
            "looking cheaper. That planner decision, not the ANN index "
            "itself, is what actually saved this query."
        )


if __name__ == "__main__":
    main()
