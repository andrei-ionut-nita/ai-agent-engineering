# Lesson 28: Three status views, and when to reach for each

## Where we left off

This course has used `graph.status()` since Lesson 2, as a quick
"is anything built yet" check. There are two more status functions
worth knowing before the capstone, each answering a narrower, more
operational question, the pggraph equivalent of Postgres's own
`pg_stat_statements`.

## `graph.status()`: the graph, right now

```sql
SELECT node_count, edge_count, memory_used_mb, sync_status, read_only
FROM graph.status();
```

The general-purpose view this course has used throughout: how big is
the graph, is it syncing, is it in a read-only state. The right first
call when something seems off, before reaching for either function
below.

## `graph.resource_status()`: the most recent operation's cost

```sql
SELECT operation, memory_budget_bytes, memory_peak_bytes, rows
FROM graph.resource_status();
```

Reports on whatever pggraph operation last ran in this session,
`'build'` here, how much memory it was allowed (`memory_budget_bytes`,
tied to the `graph.memory_limit_mb` setting mentioned back in Lesson
5), how much it actually peaked at, and how many rows it processed.
Useful for answering "was that build/traversal/vacuum close to its
memory limit", before it becomes a production incident instead of a
number you checked proactively.

## `graph.projection_status()`: the durable artifact on disk

```sql
SELECT manifest_generation, artifact_bytes, segment_count, compaction_recommended
FROM graph.projection_status();
```

Recall from the README's architecture notes (Lesson 1): persisted
builds write a `.pggraph` artifact to disk, mapped read-only across
backends. This is the status of *that* artifact, not the in-memory
graph, how many bytes it takes up, how many segments it's split into,
and whether pggraph thinks it's time to compact them
(`compaction_recommended`). This matters once a graph has been through
enough rebuilds and vacuums that its on-disk artifact has fragmented,
the same idea as Postgres table bloat, and `graph.projection_compact()`
(not run here, mentioned for completeness) is the fix.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/03_advanced/28_monitoring_graph_health/lesson.py
```

## Expected output

```
status(): node_count=11, edge_count=16, sync_status=idle, read_only=False
resource_status(): [('build', 2147483648, ..., 79)]
projection_status(): manifest_generation=1, segment_count=0, compaction_recommended=False
```

## Checkpoint

- **`graph.status()`**: the graph's current state, the first thing to
  check when something seems off.
- **`graph.resource_status()`**: cost of the most recent operation in
  this session, memory budget vs. actual peak.
- **`graph.projection_status()`**: health of the durable on-disk
  artifact, separate from the in-memory graph, watch
  `compaction_recommended` on a long-lived graph.

If anything here still feels unclear, ask before moving to Lesson 29,
this course's capstone.
