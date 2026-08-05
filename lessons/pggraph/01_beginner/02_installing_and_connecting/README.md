# Lesson 2: The pggraph Postgres container, and a quirk of its database name

## Where we left off

Lesson 1 connected to the pggraph Postgres container and confirmed the
`graph` extension was already enabled. This lesson looks at how that
container is set up, since it's built slightly differently than the
pgvector course's, and connecting to the wrong database name is the
single most common mistake when starting out with pggraph.

## Two separate Postgres containers

This project's `docker-compose.yml` runs two independent Postgres
containers side by side: `db` (pgvector, port `5433`) and `graph_db`
(pggraph, port `5434`). They don't share data or a network namespace
beyond both being reachable from your machine. `PGGRAPH_DSN` in `.env`
points at the second one:

```
PGGRAPH_DSN=postgresql://postgres:postgres@localhost:5434/graph
```

## Why the database is named `graph`, not `ai_learning`

Every other DSN in this project points at a database named
`ai_learning`. This one doesn't. pggraph's own Docker image bakes in
startup scripts (the ones that schedule its background maintenance jobs
via `pg_cron`) that are hardcoded to run against a database literally
named `graph`, matching the extension's own SQL schema name. Point the
DSN at any other database name and those startup scripts fail before
Postgres finishes starting. This is a property of the *image*, not of
pggraph the extension in general, if you install pggraph into an
existing Postgres yourself later (the PGXN or Homebrew path, see the
project's README), you're not bound by this.

## Confirming both containers are healthy

```python
import psycopg

for name, dsn in [
    ("pgvector", os.environ["POSTGRES_DSN"]),
    ("pggraph", os.environ["PGGRAPH_DSN"]),
]:
    with psycopg.connect(dsn, connect_timeout=3) as conn:
        print(name, conn.execute("SELECT current_database()").fetchone())
```

`graph.status()` is a lighter check specific to pggraph, it reports on
the graph itself (empty right now, nothing's been registered yet):

```sql
SELECT * FROM graph.status();
```

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/01_beginner/02_installing_and_connecting/lesson.py
```

## Expected output

```
pgvector container: database 'ai_learning'
pggraph container: database 'graph'
graph.status(): node_count=0, edge_count=0
```

## Checkpoint

- **two containers, two DSNs**: `POSTGRES_DSN` (pgvector, port 5433,
  database `ai_learning`) and `PGGRAPH_DSN` (pggraph, port 5434,
  database `graph`) are independent.
- **the database must be named `graph`**: pggraph's Docker image's own
  startup scripts require it, changing `POSTGRES_DB` for the `graph_db`
  service breaks container startup.
- **`graph.status()`**: the cheapest way to confirm the extension is
  reachable and see what's currently registered/built.

If anything here still feels unclear, ask before moving to Lesson 3.
