# Lesson 26: `pg_stat_statements`, tracking real query latency over time

## Where we left off

Every earlier lesson measured one query, once, with `EXPLAIN ANALYZE`
(Lesson 14) or `time.perf_counter()`. A running application needs the
other view: which queries, across thousands of calls over hours, are
actually slow, and how that latency behaves over time, not just in one
sample run.

## Turning it on

`pg_stat_statements` needs to be loaded when Postgres itself starts,
not just enabled with `CREATE EXTENSION`, this course's
`docker-compose.yml` now starts Postgres with:

```yaml
command: ["postgres", "-c", "shared_preload_libraries=pg_stat_statements"]
```

Then, once per database:

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

Skip the `shared_preload_libraries` step and `CREATE EXTENSION` still
succeeds, but querying the view fails with an explicit error saying
so, worth knowing, since it's an easy step to forget when setting this
up on a server you don't control the startup flags for.

## What it tracks

```sql
SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time,
    rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10
```

Every distinct query shape (parameter values normalized to `$1`, `$2`,
...) gets one row: how many times it's run, its mean and max execution
time, total rows returned, since the last reset. This is the real-world
version of Lesson 14's `EXPLAIN ANALYZE`, instead of "how did this one
query run just now," it's "how has this query actually been performing
across every real call so far."

## Using it to find the vector query that's actually slow

```sql
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
WHERE query ILIKE '%<=>%' OR query ILIKE '%embedding%'
ORDER BY mean_exec_time DESC
```

Filtering for the distance operators or an `embedding` column name
surfaces exactly the vector searches in your application, ranked by
real average cost, which is the query to `EXPLAIN ANALYZE` next
(Lesson 14) if one of them looks wrong, and the query to watch after
changing `ef_search`, `probes`, or an index type, to confirm a tuning
change actually helped in practice, not just in one isolated test.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/03_advanced/26_monitoring_and_observability/lesson.py
```

## Checkpoint

- **`shared_preload_libraries`**: `pg_stat_statements` needs this set at
  server startup, `CREATE EXTENSION` alone isn't enough.
- **`pg_stat_statements`**: one row per distinct query shape, tracking
  call count and execution time across the server's real, actual
  traffic.
- Use it to find which vector queries are actually slow in practice,
  then `EXPLAIN ANALYZE` (Lesson 14) that specific one.

If anything here still feels unclear, ask before moving to Lesson 27.
