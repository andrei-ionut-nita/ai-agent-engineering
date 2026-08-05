# Lesson 24: `maintenance_work_mem`, `CONCURRENTLY`, and rebuilding after bulk loads

## Where we left off

Lessons 11-12 built indexes on data that was already loaded, without
worrying about how long that build takes or what it locks. On real
data volumes, both questions matter: a slow build costs time, and by
default `CREATE INDEX` blocks writes to the table for its entire
duration.

## `maintenance_work_mem`: more memory, faster builds

```sql
SET maintenance_work_mem = '512MB';
```

Building an `hnsw` or `ivfflat` index is memory-intensive work (HNSW in
particular holds a lot of graph structure in memory while it builds).
`maintenance_work_mem` caps how much memory operations like `CREATE
INDEX` are allowed to use; too little, and the build has to spill work
to disk, dramatically slower. This lesson's script times the identical
build at a low and a high setting, on the same 20,000-row table, expect
a meaningfully faster build with more memory available. This setting is
safe to raise just for the session running the build (`SET`, not a
permanent server change), Postgres's default is often too conservative
for a dedicated bulk-load moment.

## `CONCURRENTLY`: building without blocking writes

```sql
CREATE INDEX CONCURRENTLY ON items USING hnsw (embedding vector_cosine_ops);
```

Plain `CREATE INDEX` takes a lock that blocks other transactions from
writing to the table until the build finishes, fine for a one-off
script, not fine for an index you're adding to a table a live
application keeps writing to. `CONCURRENTLY` builds the index without
that lock, at the cost of a slower build overall, and it cannot run
inside an explicit multi-statement transaction block, each `CREATE
INDEX CONCURRENTLY` is its own standalone statement. This is the one
you actually want in a running production system.

## Why `ivfflat` sometimes needs a full rebuild later

Recall Lesson 11: `ivfflat` clusters vectors into `lists` groups at
build time, using whatever data existed *then*. Load a large amount of
new data afterward, and those original clusters may no longer reflect
the data's real shape well, hurting recall gradually, silently, with no
error anywhere. The fix is `REINDEX`:

```sql
REINDEX INDEX CONCURRENTLY items_embedding_idx;
```

There's no fixed rule for "how much new data is too much" before a
rebuild is worth it, it depends on how differently the new data is
distributed from what the index was built on. `hnsw` doesn't have this
particular problem (new vectors are inserted directly into the existing
graph, not reassigned to stale pre-computed clusters), one more reason
it's usually the stronger default (Lesson 12).

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/03_advanced/24_index_build_performance_and_maintenance/lesson.py
```

## Checkpoint

- **`maintenance_work_mem`**: raise it (per-session, via `SET`) before a
  bulk index build, more memory usually means a meaningfully faster
  build.
- **`CREATE INDEX CONCURRENTLY`**: builds without blocking writes,
  slower overall, but the one to use against a live table.
- `ivfflat` can need a full `REINDEX` after large data growth, its
  original clusters go stale; `hnsw` doesn't have this problem.

If anything here still feels unclear, ask before moving to Lesson 25.
