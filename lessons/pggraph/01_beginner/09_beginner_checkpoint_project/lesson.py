"""
Lesson 9 (Beginner Checkpoint): Company Directory Explorer.

Combines graph.search() and graph.get_neighbors() (Lessons 7-8) into a
tiny two-function directory lookup: find a person, then find their
coworkers, using no hand-written SQL joins.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    docker compose up -d
    uv run python lessons/pggraph/01_beginner/09_beginner_checkpoint_project/lesson.py
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


def find_person(conn: psycopg.Connection, name: str) -> tuple[str, dict] | None:
    """Finds a person by exact name match. Returns (node_id, node) or
    None if nobody matched."""
    row = conn.execute(
        """
        SELECT node_id, node FROM graph.search(
            'name', %s,
            table_filter := 'public.people'::regclass,
            mode := 'exact'
        )
        """,
        (name,),
    ).fetchone()
    return row


def company_of(conn: psycopg.Connection, person_id: str) -> tuple[str, dict] | None:
    """First hop: person -> their company, direction 'out'."""
    return conn.execute(
        """
        SELECT node_id, node FROM graph.get_neighbors(
            graph_name := 'default', label := 'people', id := %s,
            direction := 'out', edge_types := ARRAY['works_at']
        )
        """,
        (person_id,),
    ).fetchone()


def coworkers_of(
    conn: psycopg.Connection, person_id: str, company_id: str
) -> list[tuple[str, dict]]:
    """Second hop: company -> everyone there, direction 'in', minus the
    original person."""
    rows = conn.execute(
        """
        SELECT node_id, node FROM graph.get_neighbors(
            graph_name := 'default', label := 'companies', id := %s,
            direction := 'in', edge_types := ARRAY['works_at']
        )
        """,
        (company_id,),
    ).fetchall()
    return [(node_id, node) for node_id, node in rows if node_id != person_id]


def main() -> None:
    dsn = os.environ["PGGRAPH_DSN"]

    with psycopg.connect(dsn, autocommit=True) as conn:
        setup_and_build(conn)

        person_id, person = find_person(conn, "Alice")
        company_id, company = company_of(conn, person_id)
        print(f"Found: {person['name']} ({person_id}) at {company['name']} ({company_id})")

        print(f"Coworkers at {company['name']}:")
        for coworker_id, coworker in coworkers_of(conn, person_id, company_id):
            print(f"  - {coworker['name']} ({coworker_id})")


if __name__ == "__main__":
    main()
