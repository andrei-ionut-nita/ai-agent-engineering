"""
Lesson 25: graph.add_sync_policy(), graph.run_due_jobs(), graph.sync_health().

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    docker compose up -d
    uv run python lessons/pggraph/03_advanced/25_sync_policies_and_scheduled_jobs/lesson.py
"""

import os
import time

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

        # A 1-second interval so the policy is already due by the time
        # run_due_jobs() runs below, a real policy would use something
        # like 60 or 300.
        _policy_id, _job_id, interval, enabled = conn.execute("""
            SELECT policy_id, job_id, schedule_interval_secs, enabled
            FROM graph.add_sync_policy('default', schedule_interval_secs := 1)
        """).fetchone()
        print(f"Sync policy created: schedule_interval_secs={interval}, enabled={enabled}")

        conn.execute("UPDATE people SET seniority_years = 99 WHERE id = 'p1'")
        time.sleep(1.5)

        # Rerunning this script adds another policy each time (policies
        # aren't cleared by graph.reset()), so the raw job list grows
        # across reruns, summarize instead of printing it directly.
        due = conn.execute(
            "SELECT status, rows_applied FROM graph.run_due_jobs()"
        ).fetchall()
        all_completed = all(status == "completed" for status, _ in due)
        total_rows_applied = sum(rows for _, rows in due)
        print(
            f"Due jobs run: {len(due)}, all completed={all_completed}, "
            f"total rows_applied={total_rows_applied}"
        )

        sync_mode, pending_sync_rows, apply_sync_recommended = conn.execute(
            "SELECT sync_mode, pending_sync_rows, apply_sync_recommended FROM graph.sync_health()"
        ).fetchone()
        print(
            f"sync_health(): sync_mode={sync_mode}, "
            f"pending_sync_rows={pending_sync_rows}, "
            f"apply_sync_recommended={apply_sync_recommended}"
        )


if __name__ == "__main__":
    main()
