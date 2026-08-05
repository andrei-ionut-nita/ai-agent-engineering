"""
Lesson 3: creating the companies/people schema and registering it as nodes.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    docker compose up -d
    uv run python lessons/pggraph/01_beginner/03_registering_tables_as_nodes/lesson.py
"""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    dsn = os.environ["PGGRAPH_DSN"]

    with psycopg.connect(dsn, autocommit=True) as conn:
        # Clears any graph state from a previous run of this or a later
        # lesson, so this script is safe to run repeatedly and on its own.
        conn.execute("SELECT graph.reset()")

        # Ordinary Postgres DDL, nothing pggraph-specific. This is the
        # schema every lesson in this course builds on. CREATE TABLE IF
        # NOT EXISTS + TRUNCATE, not DROP/CREATE: a table's Postgres OID
        # changes every time it's dropped and recreated, and later
        # lessons register edges/filters against that OID, TRUNCATE
        # keeps the OID stable across reruns.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id text PRIMARY KEY,
                name text NOT NULL
            )
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
                ('c1', 'Acme Bank'),
                ('c2', 'Northwind Trading')
        """)
        conn.execute("""
            INSERT INTO people (id, name, company_id) VALUES
                ('p1', 'Alice', 'c1'),
                ('p2', 'Bob', 'c1'),
                ('p3', 'Carol', 'c2')
        """)

        # Registering a table doesn't build anything yet, it just tells
        # pggraph "this is a node type, here's its ID and searchable
        # columns" for when graph.build() runs later.
        conn.execute("""
            SELECT graph.add_table(
                'public.companies'::regclass,
                id_column := 'id',
                columns := ARRAY['name']
            )
        """)
        conn.execute("""
            SELECT graph.add_table(
                'public.people'::regclass,
                id_column := 'id',
                columns := ARRAY['name']
            )
        """)

        rows = conn.execute("""
            SELECT table_name, id_columns, columns
            FROM graph.registered_tables()
            ORDER BY table_name
        """).fetchall()

    print("Registered tables:")
    for table_name, id_columns, columns in rows:
        print(f"  {table_name:<10} id_columns={id_columns}  columns={columns}")


if __name__ == "__main__":
    main()
