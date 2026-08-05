# Lesson 24: Building without blocking, and cleaning up after writes

## Where we left off

Every `graph.build()` call in this course so far has been synchronous,
your query waits until the whole graph is compiled. Fine for this
course's five-to-eleven-row example, not fine for a graph with millions
of rows, where a build might take real time. This lesson covers the
async alternative, plus the two maintenance operations that keep a
long-lived graph healthy.

## `graph.build_async_graph()`: fire, then poll

```sql
SELECT build_id, status FROM graph.build_async_graph('default');
-- build_id=... status=queued

SELECT status, nodes_loaded, edges_loaded FROM graph.build_status('<build_id>');
-- status=completed  nodes_loaded=11  edges_loaded=16
```

`build_async_graph()` launches a background worker and returns
immediately with a `build_id` and `status := 'queued'`, it doesn't wait
for the build to finish. `graph.build_status(build_id)` is how you
check progress afterward, `status` moves from `queued` to (eventually)
`completed`, with `progress_phase`/`progress_message` available for a
finer-grained look while it's running. For this course's tiny example
graph the whole thing finishes almost immediately either way, the value
of the async path only shows up at real scale.

## `graph.vacuum()`: rebuild from source, cleanly

```sql
SELECT * FROM graph.vacuum();
-- nodes_before=11  nodes_after=11  tombstones_removed=0  edges_rebuilt=16
```

Deletes accumulate as tombstones (marked-removed, not physically gone)
in a long-running graph with a mutable overlay (Lesson 22) or heavy
sync activity (Lesson 18); `graph.vacuum()` rebuilds cleanly from
source and reports what it cleared, `0` here because this course's
example graph has no deletes yet.

## `graph.maintenance()`: sync, then vacuum, in one call

```sql
SELECT job_id, status, sync_rows_applied, nodes_after, edges_after
FROM graph.maintenance();
-- status=completed  sync_rows_applied=0  nodes_after=11  edges_after=16
```

This is `graph.apply_sync()` (Lesson 18) and `graph.vacuum()` chained
into one maintenance pass, the kind of thing you'd run on a schedule
(Lesson 25 covers scheduling it) rather than after every individual
write. `concurrently := true` runs it as a background job instead of
blocking the calling session, the same async idea as
`build_async_graph()`, applied to maintenance instead of the initial
build.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/03_advanced/24_async_builds_and_maintenance/lesson.py
```

## Expected output

```
Async build: build_id=<uuid> status=queued
After polling: status=completed, nodes_loaded=11, edges_loaded=16
Vacuum: nodes_before=11, nodes_after=11, tombstones_removed=0
Maintenance: status=completed, sync_rows_applied=0, nodes_after=11, edges_after=16
```

## Checkpoint

- **`graph.build_async_graph()` / `graph.build_status(build_id)`**:
  non-blocking build plus polling, for graphs too large to build
  synchronously.
- **`graph.vacuum()`**: rebuilds from source, clearing tombstones left
  by deletes.
- **`graph.maintenance()`**: sync + vacuum in one call, the operation to
  put on a schedule rather than run after every write.

If anything here still feels unclear, ask before moving to Lesson 25.
