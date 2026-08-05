"""
Lesson 7: graph.get_neighbors(), one hop out from a single node.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    docker compose up -d
    uv run python lessons/pggraph/01_beginner/07_single_hop_neighbors/lesson.py
"""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def setup_and_build(conn: psycopg.Connection) -> None:
    """Recreates and builds the schema from Lessons 3-5."""
    conn.execute("SELECT graph.reset()")
    # CREATE TABLE IF NOT EXISTS + TRUNCATE, not DROP/CREATE: pggraph's
    # edge registrations are tied to a table's Postgres OID. Dropping
    # and recreating a table gives it a new OID on every run, which
    # orphans the registration made against the old one, TRUNCATE keeps
    # the table (and its OID) in place, so rerunning this script stays
    # safe.
    conn.execute("CREATE TABLE IF NOT EXISTS companies (id text PRIMARY KEY, name text NOT NULL)")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id text PRIMARY KEY,
            name text NOT NULL,
            company_id text REFERENCES companies(id)
        )
    """)
    conn.execute("TRUNCATE TABLE people, companies CASCADE")
    conn.execute("""
        INSERT INTO companies (id, name) VALUES
            ('c1', 'Acme Bank'), ('c2', 'Northwind Trading')
    """)
    conn.execute("""
        INSERT INTO people (id, name, company_id) VALUES
            ('p1', 'Alice', 'c1'), ('p2', 'Bob', 'c1'), ('p3', 'Carol', 'c2')
    """)
    conn.execute("""
        SELECT graph.add_table('public.companies'::regclass,
            id_column := 'id', columns := ARRAY['name'])
    """)
    conn.execute("""
        SELECT graph.add_table('public.people'::regclass,
            id_column := 'id', columns := ARRAY['name'])
    """)
    conn.execute("""
        SELECT graph.add_edge(
            from_table := 'public.people'::regclass,
            from_column := 'company_id',
            to_table := 'public.companies'::regclass,
            to_column := 'id',
            label := 'works_at',
            bidirectional := true
        )
    """)
    conn.execute("SELECT graph.build()")


def main() -> None:
    dsn = os.environ["PGGRAPH_DSN"]

    with psycopg.connect(dsn, autocommit=True) as conn:
        setup_and_build(conn)

        # direction must be 'out', 'in', or 'any', pggraph rejects other
        # spellings outright.
        rows = conn.execute("""
            SELECT node_id, depth, node
            FROM graph.get_neighbors(
                graph_name := 'default',
                label := 'people',
                id := 'p1',
                direction := 'out',
                edge_types := ARRAY['works_at']
            )
        """).fetchall()

    print("Alice's direct neighbors (out, works_at):")
    for node_id, depth, node in rows:
        print(f"  {node_id}  depth={depth}  {node}")


if __name__ == "__main__":
    main()
