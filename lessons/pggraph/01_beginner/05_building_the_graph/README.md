# Lesson 5: graph.build(), and what "compiling" a graph means

## Where we left off

Lesson 4 registered `companies`, `people`, and the `works_at` edge
between them. All of that is still just metadata, pggraph knows the
*shape* of the graph but hasn't read a single row yet. This lesson runs
`graph.build()`, the step that actually compiles a queryable graph.

## `graph.build()`: reading your tables into memory once

```sql
SELECT * FROM graph.build();
```

This reads every row of every registered table and edge, and compiles
them into an in-memory structure (a compressed sparse row, or CSR,
adjacency store, more on that in a moment) that later traversal queries
walk directly, instead of re-querying and re-joining your tables on
every call. It returns a small report:

```
nodes_loaded=5  edges_loaded=6  build_time_ms=48.7  sync_mode=trigger
```

Five nodes: 2 companies + 3 people. Six edges, not three, because
`bidirectional := true` (Lesson 4) makes each `works_at` relationship
walkable in both directions, and pggraph stores that as two directed
edges internally, one each way.

## What CSR buys you

"Compressed sparse row" just means: for every node, its neighbors are
stored as one contiguous slice of an array, so "who is this node
connected to" is a direct memory lookup, not a search. That's the whole
performance story behind pggraph, traversal becomes array scanning
instead of repeated SQL joins. You don't manage this structure
yourself, it's what `graph.build()` produces and what every query
function in this course reads from.

## `sync_mode = 'trigger'`

Notice the build output includes `sync_mode=trigger`, and a warning
that it installed triggers on both tables. By default, `graph.build()`
sets your registered tables up to notify pggraph automatically when
rows change, so the graph can stay current without you rebuilding by
hand every time. Lesson 18 covers what those triggers do and how to
apply the changes they queue up.

## Confirming the build with graph.status()

```sql
SELECT node_count, edge_count, edge_types FROM graph.status();
```

This is the same function from Lesson 2, but no longer empty.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/01_beginner/05_building_the_graph/lesson.py
```

## Expected output

```
Build report: nodes_loaded=5, edges_loaded=6, sync_mode=trigger
graph.status(): node_count=5, edge_count=6, edge_types=['works_at']
```

## Checkpoint

- **`graph.build()`**: compiles every registered table/edge into an
  in-memory CSR graph, this is the step that makes traversal fast.
- **why 6 edges from 3 relationships**: `bidirectional := true` stores
  each relationship as two directed edges internally.
- **`sync_mode = 'trigger'`**: the default, installs triggers so pggraph
  notices row changes; covered fully in Lesson 18.

If anything here still feels unclear, ask before moving to Lesson 6.
