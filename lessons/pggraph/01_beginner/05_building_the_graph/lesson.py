"""
Lesson 5: graph.build(), compiling the registered schema into a graph.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    docker compose up -d
    uv run python lessons/pggraph/01_beginner/05_building_the_graph/lesson.py
"""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def setup_schema(conn: psycopg.Connection) -> None:
    """Recreates the schema and registration from Lessons 3-4, so this
    lesson can run on its own."""
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


def main() -> None:
    dsn = os.environ["PGGRAPH_DSN"]

    with psycopg.connect(dsn, autocommit=True) as conn:
        setup_schema(conn)

        # The new step: compile everything registered above into an
        # in-memory, traversable graph.
        nodes_loaded, edges_loaded, _build_ms, _mem_mb, sync_mode, _mode = conn.execute(
            "SELECT nodes_loaded, edges_loaded, build_time_ms, memory_used_mb, "
            "sync_mode, projection_mode FROM graph.build()"
        ).fetchone()
        print(
            f"Build report: nodes_loaded={nodes_loaded}, "
            f"edges_loaded={edges_loaded}, sync_mode={sync_mode}"
        )

        node_count, edge_count, edge_types = conn.execute(
            "SELECT node_count, edge_count, edge_types FROM graph.status()"
        ).fetchone()
        print(
            f"graph.status(): node_count={node_count}, "
            f"edge_count={edge_count}, edge_types={edge_types}"
        )


if __name__ == "__main__":
    main()
