# Lesson 29: Capstone — A Relationship-Aware Context API

## What this is

A small FastAPI service wrapping this course's `capstone_companies`/`capstone_people`
graph in three endpoints: add a person, get everything directly
connected to a person, and find how two people are connected. This is
the shape of thing pggraph's own docs point at directly, an AI agent's
"give me relevant context around this entity" endpoint, backed by
ordinary Postgres tables and a compiled graph instead of a hand-rolled
recursive query or a separate graph database.

## What it does

`lifespan()` builds the graph once at startup (same shape as Lesson
10's schema, `works_at`/`reports_to`), the same pattern FastAPI's
`lifespan` handler has used throughout this repo's courses, setup that
runs once, not per-request. The tables are named `capstone_companies`/
`capstone_people`, not `companies`/`people`, deliberately, so this
capstone doesn't collide with whatever state earlier lessons left in
the shared `graph` database (the same reason pgvector's own capstone
uses a dedicated `capstone_notes` collection name). Three endpoints:

- `POST /people` — inserts (or updates) a person row. No explicit sync
  call afterward, on purpose.
- `GET /context/{person_id}` — `graph.get_node()` for the person plus
  `graph.get_neighbors(direction := 'any')` for everything one hop
  away, company and manager/reports together.
- `GET /connection?from_name=X&to_name=Y` — `graph.connection()`,
  searching both people by name and returning the path between them as
  one readable string.

## Where each piece came from

- Schema, table/edge registration, `graph.build()` — Lesson 10's setup,
  trimmed to `capstone_companies`/`capstone_people` only (no `projects`/`subsidiary_of`,
  this capstone didn't need them).
- `POST /people` writing straight to the table, with no
  `graph.apply_sync()` call, and `GET /context` seeing the new person
  immediately anyway — Lesson 18's sync overlay, writes are visible to
  queries before you explicitly sync anything.
- `graph.get_node()` / `graph.get_neighbors()` — Lessons 6-7.
- `graph.connection()` — Lesson 15.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/03_advanced/29_advanced_capstone_project/lesson.py
```

To run it as a real, live server instead (then visit
`http://127.0.0.1:8000/docs` for interactive API docs):

```bash
cd lessons/pggraph/03_advanced/29_advanced_capstone_project
uvicorn lesson:app --reload
```

## Expected output

```
POST /people -> {'added': 'p4'}

GET /context/p4:
  person: {'id': 'p4', 'name': 'Dan', 'company_id': 'c1', 'manager_id': 'p2'}
  directly connected to: [{'table': 'capstone_companies', 'id': 'c1', 'name': 'Acme Bank'}, {'table': 'capstone_people', 'id': 'p2', 'name': 'Bob'}]

GET /connection?from_name=Dan&to_name=Alice:
  capstone_people:p4 --works_at--> capstone_companies:c1 | capstone_companies:c1 --works_at--> capstone_people:p1
```

(The connection path may come back through `works_at` or through
`reports_to`, both are exactly two hops from Dan to Alice, `works_at`
via their shared company, `reports_to` via Dan's manager Bob. Which one
`graph.connection()` returns is not guaranteed to be stable between
runs when two paths tie, this course observed both across repeated
runs of this exact lesson. Worth remembering if you extend
`/connection` to prefer one relationship type over another, filter
`edge_types` yourself rather than relying on tie-breaking order.)

## Try this yourself

- Add a `GET /people/{person_id}/search?q=...` endpoint using
  `graph.search()` (Lesson 8) to find people by partial name match.
- Extend `/context` to accept a `depth` query parameter and use
  `graph.expand()` (Lesson 14) instead of `get_neighbors()`, returning
  more than one hop.
- Add a `DELETE /people/{person_id}` endpoint, then check
  `graph.status()`'s `pending_sync_rows` (Lesson 18) immediately after,
  to see the delete queued the same way an insert or update would.
- This is the last lesson in the course, go back to the project root
  [README.md](../../../../README.md) and skim the other six courses,
  this one's `capstone_companies`/`capstone_people` graph would slot naturally into a
  `langgraph` agent's memory layer or a `pydantic_ai` tool.
