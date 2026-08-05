"""
Lesson 26: pg_stat_statements, tracking real query latency across many
calls, not just one sampled run.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first, and has been
restarted since docker-compose.yml added shared_preload_libraries):

    docker compose up -d
    uv run python lessons/pgvector/03_advanced/26_monitoring_and_observability/lesson.py
"""

import os

import numpy as np
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from pgvector.utils import Vector

load_dotenv()

DIMENSIONS = 768
ROW_COUNT = 2_000
SEED = 13
QUERY_REPEATS = 20


def main() -> None:
    rng = np.random.default_rng(SEED)
    vectors = rng.normal(size=(ROW_COUNT, DIMENSIONS)).astype("float32")

    dsn = os.environ["POSTGRES_DSN"]
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)

        try:
            conn.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements")
        except psycopg.errors.FeatureNotSupported as exc:
            raise SystemExit(
                "pg_stat_statements needs shared_preload_libraries set at "
                "server startup. Run `docker compose up -d` to pick up the "
                "updated docker-compose.yml, then try again."
            ) from exc

        conn.execute("DROP TABLE IF EXISTS monitored_items")
        conn.execute(
            f"CREATE TABLE monitored_items (id bigserial PRIMARY KEY, embedding vector({DIMENSIONS}))"
        )
        with conn.cursor() as cur, cur.copy(
            "COPY monitored_items (embedding) FROM STDIN"
        ) as copy:
            for vector in vectors:
                copy.write_row((Vector(vector),))
        conn.execute("CREATE INDEX ON monitored_items USING hnsw (embedding vector_cosine_ops)")

        conn.execute("SELECT pg_stat_statements_reset()")

        # Run the same vector search shape many times, real applications
        # run the same query shape thousands of times with different
        # parameter values, this simulates that.
        for _ in range(QUERY_REPEATS):
            query_vector = Vector(rng.normal(size=DIMENSIONS).astype("float32"))
            conn.execute(
                "SELECT id FROM monitored_items ORDER BY embedding <=> %s LIMIT 5",
                (query_vector,),
            ).fetchall()

        rows = conn.execute(
            """
            SELECT query, calls, mean_exec_time, max_exec_time
            FROM pg_stat_statements
            WHERE query ILIKE %s
            ORDER BY mean_exec_time DESC
            """,
            ("%embedding%",),
        ).fetchall()

        print(f"Ran the same vector search shape {QUERY_REPEATS} times.\n")
        print("pg_stat_statements' view of it:\n")
        for query, calls, mean_time, max_time in rows:
            print(f"  query: {query[:80]}...")
            print(f"  calls: {calls}, mean: {mean_time:.3f} ms, max: {max_time:.3f} ms\n")


if __name__ == "__main__":
    main()
