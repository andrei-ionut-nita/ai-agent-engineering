# Lesson 22: Writing through the graph, with a mutable overlay

## Where we left off

Every graph in this course so far has been read-only after
`graph.build()`, all the writes happened through ordinary `INSERT`/
`UPDATE` on the underlying tables (Lesson 18's sync overlay picking
those up). GQL can also write directly, `CREATE`, `SET`, `MERGE`,
`DELETE`, `DETACH DELETE`, but only if the graph was built in a
different mode.

## Two settings you need first

```sql
SET graph.mutable_enabled = on;
SELECT * FROM graph.build('mutable_overlay');
```

`graph.mutable_enabled` is a Postgres configuration parameter (a GUC),
off by default, a deliberate safety gate: GQL writes are opt-in at the
session level, not something a stray query can do by accident.
`graph.build('mutable_overlay')` is the same build call from every
earlier lesson, with an explicit mode this time, `'csr_readonly'` (the
default used everywhere so far) is read-optimized and rejects writes
outright; `'mutable_overlay'` keeps a separate writable layer on top
for GQL's write clauses to land in.

## `CREATE`, `SET`, and reading it back

```sql
SELECT row FROM graph.gql(
  'CREATE (c:people {id: $id, name: $name}) RETURN c',
  params := '{"id": "p9", "name": "Frank"}'::jsonb
);

SELECT row FROM graph.gql(
  'MATCH (p:people {id: $id}) SET p.seniority_years = $years RETURN p.name, p.seniority_years',
  params := '{"id": "p9", "years": 1}'::jsonb
);
```

`CREATE` makes a new node directly in the graph's overlay, not (only)
in the underlying `people` table, this is a graph-first write, the
inverse direction from every other lesson's "table changes, graph
follows." `SET` updates a property the same way. Immediately after,
`MATCH ... RETURN p.name` finds Frank, same as any other registered
node.

## Where this fits, realistically

This course's running example is registered-table-driven throughout,
because that matches how most existing applications already store
data. GQL writes matter most when the graph itself is closer to the
primary interface, an AI agent maintaining its own memory graph
directly, for instance, rather than mediating every write through a
separate table schema. `mutable_overlay` mode is what makes that usage
pattern possible without giving up everything else pggraph does.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/03_advanced/22_gql_writes_and_mutable_overlay/lesson.py
```

## Expected output

```
Created via GQL CREATE: Frank
After GQL SET: Frank, seniority_years=1
```

## Checkpoint

- **`graph.mutable_enabled`**: a session-level GUC, off by default,
  must be explicitly turned on before any GQL write will run.
- **`graph.build('mutable_overlay')`**: the build mode that enables
  writes; the default `'csr_readonly'` mode rejects them.
- **GQL writes land in the graph directly**, not only in the
  underlying registered table, the reverse direction from every other
  lesson in this course.

If anything here still feels unclear, ask before moving to Lesson 23.
