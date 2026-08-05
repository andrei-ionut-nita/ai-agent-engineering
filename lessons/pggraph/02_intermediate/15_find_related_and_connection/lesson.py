"""
Lesson 15: graph.find_related() and graph.connection(), starting from a
search instead of a known ID.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    docker compose up -d
    uv run python lessons/pggraph/02_intermediate/15_find_related_and_connection/lesson.py
"""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def setup_and_build(conn: psycopg.Connection) -> None:
    """Builds this tier's extended schema: companies with subsidiaries,
    people with a reporting chain, and a projects table. Every lesson in
    this tier calls this, so each one runs standalone."""
    conn.execute("SELECT graph.reset()")

    # CREATE TABLE IF NOT EXISTS + ALTER ... ADD COLUMN IF NOT EXISTS +
    # TRUNCATE, not DROP/CREATE: pggraph's filter-column and edge
    # registrations (below) are tied to a table's Postgres OID.
    # Dropping and recreating a table gives it a new OID on every run,
    # which orphans any registration made against the old one. The
    # beginner tier already created "companies"/"people" with fewer
    # columns, ALTER ... ADD COLUMN IF NOT EXISTS grows them in place
    # (same OID) instead of failing or requiring a drop, and TRUNCATE
    # clears rows without touching the table itself.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS companies (id text PRIMARY KEY, name text NOT NULL)
    """)
    conn.execute("""
        ALTER TABLE companies ADD COLUMN IF NOT EXISTS
            parent_company_id text REFERENCES companies(id)
    """)
    conn.execute("ALTER TABLE companies ADD COLUMN IF NOT EXISTS ownership_pct numeric")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id text PRIMARY KEY,
            name text NOT NULL,
            company_id text REFERENCES companies(id)
        )
    """)
    conn.execute("""
        ALTER TABLE people ADD COLUMN IF NOT EXISTS
            manager_id text REFERENCES people(id)
    """)
    conn.execute("""
        ALTER TABLE people ADD COLUMN IF NOT EXISTS
            seniority_years int NOT NULL DEFAULT 0
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id text PRIMARY KEY,
            name text NOT NULL,
            lead_person_id text REFERENCES people(id)
        )
    """)
    conn.execute("TRUNCATE TABLE projects, people, companies CASCADE")

    conn.execute("""
        INSERT INTO companies (id, name, parent_company_id, ownership_pct) VALUES
            ('c1', 'Acme Bank', NULL, NULL),
            ('c2', 'Northwind Trading', NULL, NULL),
            ('c3', 'Acme Capital', 'c1', 100),
            ('c4', 'Acme Wealth', 'c3', 80),
            ('c5', 'Solo Ventures', NULL, NULL)
    """)
    conn.execute("""
        INSERT INTO people (id, name, company_id, manager_id, seniority_years) VALUES
            ('p1', 'Alice', 'c1', NULL, 12),
            ('p2', 'Bob', 'c1', 'p1', 6),
            ('p3', 'Carol', 'c2', NULL, 9),
            ('p4', 'Dan', 'c1', 'p2', 2),
            ('p5', 'Eve', 'c3', NULL, 4)
    """)
    conn.execute("""
        INSERT INTO projects (id, name, lead_person_id) VALUES
            ('pr1', 'Ledger Migration', 'p2')
    """)

    conn.execute("""
        SELECT graph.add_table('public.companies'::regclass,
            id_column := 'id', columns := ARRAY['name'])
    """)
    conn.execute("""
        SELECT graph.add_table('public.people'::regclass,
            id_column := 'id', columns := ARRAY['name', 'seniority_years'])
    """)
    conn.execute("""
        SELECT graph.add_table('public.projects'::regclass,
            id_column := 'id', columns := ARRAY['name'])
    """)

    conn.execute("""
        SELECT graph.add_edge(
            from_table := 'public.people'::regclass, from_column := 'company_id',
            to_table := 'public.companies'::regclass, to_column := 'id',
            label := 'works_at', bidirectional := true
        )
    """)
    conn.execute("""
        SELECT graph.add_edge(
            from_table := 'public.people'::regclass, from_column := 'manager_id',
            to_table := 'public.people'::regclass, to_column := 'id',
            label := 'reports_to', bidirectional := false
        )
    """)
    conn.execute("""
        SELECT graph.add_edge(
            from_table := 'public.companies'::regclass, from_column := 'parent_company_id',
            to_table := 'public.companies'::regclass, to_column := 'id',
            label := 'subsidiary_of', bidirectional := false,
            weight_column := 'ownership_pct'
        )
    """)
    conn.execute("""
        SELECT graph.add_edge(
            from_table := 'public.projects'::regclass, from_column := 'lead_person_id',
            to_table := 'public.people'::regclass, to_column := 'id',
            label := 'led_by', bidirectional := true
        )
    """)
    conn.execute("""
        SELECT graph.add_filter_column('public.people'::regclass, 'seniority_years', 'numeric')
    """)

    conn.execute("SELECT graph.build()")


def main() -> None:
    dsn = os.environ["PGGRAPH_DSN"]

    with psycopg.connect(dsn, autocommit=True) as conn:
        setup_and_build(conn)

        related = conn.execute("""
            SELECT node_table_name, node_id FROM graph.find_related(
                property_key := 'name', property_value := 'Alice',
                source_table := 'public.people'::regclass,
                max_depth := 2,
                target_table := 'public.people'::regclass
            )
        """).fetchall()

        print("find_related('Alice', depth<=2):")
        for node_table_name, node_id in related:
            print(f"  {node_table_name}  {node_id}")

        readable_path = conn.execute("""
            SELECT readable_path FROM graph.connection(
                source_key := 'name', source_value := 'Dan',
                target_key := 'name', target_value := 'Alice',
                source_table := 'public.people'::regclass,
                target_table := 'public.people'::regclass,
                max_depth := 4
            ) LIMIT 1
        """).fetchone()[0]

        print(f"connection(Dan -> Alice): {readable_path}")


if __name__ == "__main__":
    main()
