"""
Lesson 4: registering the people -> companies foreign key as an edge.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    docker compose up -d
    uv run python lessons/pggraph/01_beginner/04_registering_edges/lesson.py
"""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def setup_schema(conn: psycopg.Connection) -> None:
    """Recreates Lesson 3's schema and table registration, so this
    lesson can run on its own, without depending on Lesson 3 having
    just been run."""
    conn.execute("SELECT graph.reset()")
    # CREATE TABLE IF NOT EXISTS + TRUNCATE, not DROP/CREATE: pggraph's
    # edge registrations are tied to a table's Postgres OID. Dropping
    # and recreating a table gives it a new OID on every run, which
    # orphans the registration made against the old one, TRUNCATE keeps
    # the table (and its OID) in place, so rerunning this script stays
    # safe.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS companies (id text PRIMARY KEY, name text NOT NULL)
    """)
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


def main() -> None:
    dsn = os.environ["PGGRAPH_DSN"]

    with psycopg.connect(dsn, autocommit=True) as conn:
        setup_schema(conn)

        # The new part this lesson adds: turning the company_id foreign
        # key into a named, traversable edge.
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

        rows = conn.execute("""
            SELECT from_table, from_column, to_table, to_column, label, bidirectional
            FROM graph.registered_edges()
        """).fetchall()

    print("Registered edges:")
    for from_table, from_column, to_table, to_column, label, bidirectional in rows:
        print(
            f"  {from_table}.{from_column} -> {to_table}.{to_column}"
            f"  label={label}  bidirectional={bidirectional}"
        )


if __name__ == "__main__":
    main()
