"""
Lesson 22: GQL writes, gated behind graph.mutable_enabled and a
mutable_overlay build.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    docker compose up -d
    uv run python lessons/pggraph/03_advanced/22_gql_writes_and_mutable_overlay/lesson.py
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

        # GQL writes are off by default, both at the session level and
        # at the build-mode level, this course's only two-step opt-in.
        conn.execute("SET graph.mutable_enabled = on")
        conn.execute("SELECT * FROM graph.build('mutable_overlay')")

        created = conn.execute("""
            SELECT row FROM graph.gql(
                'CREATE (c:people {id: $id, name: $name}) RETURN c',
                params := %s::jsonb
            )
        """, ('{"id": "p9", "name": "Frank"}',)).fetchone()[0]
        print(f"Created via GQL CREATE: {created['c']['name']}")

        updated = conn.execute("""
            SELECT row FROM graph.gql(
                'MATCH (p:people {id: $id}) SET p.seniority_years = $years
                 RETURN p.name AS name, p.seniority_years AS seniority_years',
                params := %s::jsonb
            )
        """, ('{"id": "p9", "years": 1}',)).fetchone()[0]
        print(f"After GQL SET: {updated['name']}, seniority_years={updated['seniority_years']}")


if __name__ == "__main__":
    main()
