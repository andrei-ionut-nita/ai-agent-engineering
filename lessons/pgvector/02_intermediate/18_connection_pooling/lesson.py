"""
Lesson 18: connection pooling, why a real app never opens one
connection per query.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/02_intermediate/18_connection_pooling/lesson.py
"""

import os
import time

import psycopg
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

load_dotenv()

QUERY_COUNT = 50


def main() -> None:
    dsn = os.environ["POSTGRES_DSN"]

    # A brand-new connection for every query: a TCP handshake,
    # authentication, and a new Postgres backend process each time.
    t0 = time.perf_counter()
    for _ in range(QUERY_COUNT):
        with psycopg.connect(dsn) as conn:
            conn.execute("SELECT 1").fetchone()
    no_pool_time = time.perf_counter() - t0
    print(f"New connection per query ({QUERY_COUNT} queries): {no_pool_time:.3f} s")

    # A small pool of already-open connections, reused across queries.
    pool = ConnectionPool(conninfo=dsn, min_size=2, max_size=10)
    pool.wait()  # only so the timing below doesn't include pool warm-up

    t0 = time.perf_counter()
    for _ in range(QUERY_COUNT):
        with pool.connection() as conn:
            conn.execute("SELECT 1").fetchone()
    pooled_time = time.perf_counter() - t0
    print(f"Pooled connection per query ({QUERY_COUNT} queries): {pooled_time:.3f} s")

    pool.close()

    print(f"\nPooling was {no_pool_time / pooled_time:.1f}x faster here, purely from")
    print("skipping the connection setup cost on every single query.")


if __name__ == "__main__":
    main()
