# Lesson 1: What pggraph is, and why traversal belongs in Postgres

## Where we left off

The pgvector course showed one way an ordinary relational database can
grow a new superpower: give it a `vector` column type and it can search
by meaning. This course does the same trick for a different kind of
question. "Which records are related to this one?" and "how are these
two rows connected?" are graph questions, and answering them with plain
SQL usually means hand-written recursive CTEs, one per schema, that get
slower as the data grows. **pggraph** is the extension that adds
graph-native answers to those questions, on your existing tables,
without a separate database.

## What pggraph actually is

pggraph is a PostgreSQL extension (`CREATE EXTENSION graph`, package
name `pgGraph`, SQL name `graph`) that builds a derived, read-optimized
index of the relationships in your existing tables, then exposes SQL
functions like `graph.traverse()` and `graph.shortest_path()` to query
it. Your tables stay the source of truth: pggraph doesn't move your
data or ask you to model it a second time in a graph-specific store.
You tell it which tables are nodes and which foreign-key-shaped columns
are edges, it compiles that into memory as a graph, and you query the
graph instead of writing recursive SQL by hand.

## Why not just recursive SQL?

A question like "find everyone within two hops of this person" is
answerable with a `WITH RECURSIVE` query, but you'd write a new one for
every schema and every hop count, and it gets slow as the table grows
because the database re-discovers the relationships from scratch on
every run. pggraph's traversal engine instead pre-compiles adjacency
(who's connected to whom) into a compact in-memory structure once,
via `graph.build()`, so a traversal becomes a fast walk over that
structure instead of a fresh join-heavy query.

```sql
-- The kind of question pggraph answers without you writing this by hand:
-- "everyone within 2 hops of person p1, through any relationship"
SELECT * FROM graph.traverse('public.people'::regclass, 'p1', 2);
```

## What this course builds

Every lesson in this course works against the same small, growing
example: `companies` and `people` who work at them, the same schema
pggraph's own quickstart uses. You'll register those tables, build a
graph from them, and query it, first with pggraph's own SQL functions,
later (advanced tier) with GQL and Cypher-style pattern matching. By
the end you'll have used pggraph the way its authors intend it: as a
relationship-lookup layer for an AI agent's memory, not a replacement
for Postgres.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/01_beginner/01_what_is_pggraph/lesson.py
```

## Expected output

```
Connected to Postgres 17.10 (Debian 17.10-1.pgdg12+1)
Extension 'graph' is enabled, version 1.0.0
Extension 'pg_cron' is enabled, version 1.6
```

If you get a connection error instead, the pggraph Postgres container
probably isn't running yet, see the
[Troubleshooting section](../../../../README.md#troubleshooting) in
this project's root README.

## Checkpoint

- **pggraph**: a Postgres extension (`CREATE EXTENSION graph`) that
  builds a derived graph index from your existing tables and queries it
  with SQL functions, it isn't a separate graph database.
- **why not recursive SQL**: hand-written `WITH RECURSIVE` queries
  re-discover relationships on every run; pggraph pre-compiles adjacency
  once via `graph.build()` and traverses that instead.
- **this course's running example**: `companies` and `people`, the same
  schema pggraph's own quickstart uses, extended as the course goes on.

If anything here still feels unclear, ask before moving to Lesson 2.
