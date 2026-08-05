"""
Lesson 29: Advanced Capstone - a relationship-aware context API.

No new pggraph concepts, this wires Lessons 1-28 into one small web
service: the kind of "AI agent memory" endpoint pggraph's own docs
describe, given an entity, return what's directly connected to it and
how it relates to another entity, without the caller writing SQL.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure the pggraph Postgres container is running
first):

    docker compose up -d
    uv run python lessons/pggraph/03_advanced/29_advanced_capstone_project/lesson.py

To run this as a real, live server instead:

    uvicorn lesson:app --reload
"""

import os
from contextlib import asynccontextmanager

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

load_dotenv()


class PersonIn(BaseModel):
    id: str
    name: str
    company_id: str
    manager_id: str | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    dsn = os.environ["PGGRAPH_DSN"]
    conn = psycopg.connect(dsn, autocommit=True)

    conn.execute("SELECT graph.reset()")
    conn.execute("CREATE TABLE IF NOT EXISTS capstone_companies (id text PRIMARY KEY, name text NOT NULL)")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS capstone_people (
            id text PRIMARY KEY,
            name text NOT NULL,
            company_id text REFERENCES capstone_companies(id),
            manager_id text REFERENCES capstone_people(id)
        )
    """)
    conn.execute("TRUNCATE TABLE capstone_people, capstone_companies CASCADE")
    conn.execute("""
        INSERT INTO capstone_companies (id, name) VALUES
            ('c1', 'Acme Bank'), ('c2', 'Northwind Trading')
    """)
    conn.execute("""
        INSERT INTO capstone_people (id, name, company_id, manager_id) VALUES
            ('p1', 'Alice', 'c1', NULL),
            ('p2', 'Bob', 'c1', 'p1'),
            ('p3', 'Carol', 'c2', NULL)
    """)
    conn.execute("""
        SELECT graph.add_table('public.capstone_companies'::regclass,
            id_column := 'id', columns := ARRAY['name'])
    """)
    conn.execute("""
        SELECT graph.add_table('public.capstone_people'::regclass,
            id_column := 'id', columns := ARRAY['name'])
    """)
    conn.execute("""
        SELECT graph.add_edge(
            from_table := 'public.capstone_people'::regclass, from_column := 'company_id',
            to_table := 'public.capstone_companies'::regclass, to_column := 'id',
            label := 'works_at', bidirectional := true
        )
    """)
    conn.execute("""
        SELECT graph.add_edge(
            from_table := 'public.capstone_people'::regclass, from_column := 'manager_id',
            to_table := 'public.capstone_people'::regclass, to_column := 'id',
            label := 'reports_to', bidirectional := false
        )
    """)
    conn.execute("SELECT graph.build()")

    app.state.conn = conn
    yield
    conn.close()


app = FastAPI(lifespan=lifespan)


@app.post("/people")
def add_person(person: PersonIn) -> dict:
    conn = app.state.conn
    conn.execute(
        """
        INSERT INTO capstone_people (id, name, company_id, manager_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE
        SET name = EXCLUDED.name, company_id = EXCLUDED.company_id,
            manager_id = EXCLUDED.manager_id
        """,
        (person.id, person.name, person.company_id, person.manager_id),
    )
    # No graph.apply_sync() call needed here, Lesson 18: writes are
    # visible to queries immediately via pggraph's sync overlay.
    return {"added": person.id}


@app.get("/context/{person_id}")
def get_context(person_id: str) -> dict:
    conn = app.state.conn
    person_row = conn.execute(
        """
        SELECT node FROM graph.get_node(
            graph_name := 'default', label := 'capstone_people', id := %s, hydrate := true
        )
        """,
        (person_id,),
    ).fetchone()
    if person_row is None:
        raise HTTPException(status_code=404, detail=f"No person with id {person_id!r}")

    neighbors = conn.execute(
        """
        SELECT node_table_name, node_id, node ->> 'name' AS name
        FROM graph.get_neighbors(
            graph_name := 'default', label := 'capstone_people', id := %s, direction := 'any'
        )
        """,
        (person_id,),
    ).fetchall()

    return {
        "person": person_row[0],
        "directly_connected_to": [
            {"table": table, "id": node_id, "name": name}
            for table, node_id, name in neighbors
        ],
    }


@app.get("/connection")
def get_connection(from_name: str, to_name: str) -> dict:
    conn = app.state.conn
    row = conn.execute(
        """
        SELECT readable_path FROM graph.connection(
            source_key := 'name', source_value := %s,
            target_key := 'name', target_value := %s,
            source_table := 'public.capstone_people'::regclass,
            target_table := 'public.capstone_people'::regclass,
            max_depth := 6
        ) LIMIT 1
        """,
        (from_name, to_name),
    ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=404, detail=f"No connection found between {from_name!r} and {to_name!r}"
        )
    return {"path": row[0]}


def main() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/people", json={"id": "p4", "name": "Dan", "company_id": "c1", "manager_id": "p2"}
        )
        print(f"POST /people -> {response.json()}\n")

        response = client.get("/context/p4")
        context = response.json()
        print(f"GET /context/p4:")
        print(f"  person: {context['person']}")
        print(f"  directly connected to: {context['directly_connected_to']}\n")

        response = client.get("/connection", params={"from_name": "Dan", "to_name": "Alice"})
        print(f"GET /connection?from_name=Dan&to_name=Alice:")
        print(f"  {response.json()['path']}")


if __name__ == "__main__":
    main()
