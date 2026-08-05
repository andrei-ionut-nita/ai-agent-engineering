# Lesson 14: Reading `EXPLAIN ANALYZE`, confirming an index is actually used

## Where we left off

Lessons 11-12 timed queries with Python's `time.perf_counter()`, useful,
but it can't tell you *why* a query was fast or slow, or whether the
index you just built was even used. `EXPLAIN` answers that directly,
from Postgres itself.

## `EXPLAIN` versus `EXPLAIN ANALYZE`

```sql
EXPLAIN SELECT ...            -- the planner's ESTIMATE, doesn't run the query
EXPLAIN ANALYZE SELECT ...    -- ACTUALLY runs it, reports real timings
```

Plain `EXPLAIN` shows what Postgres's query planner *predicts* it will
do, useful when you don't want to actually run an expensive write.
`EXPLAIN ANALYZE` actually executes the query and reports real,
measured timings alongside the plan, that's almost always what you
want while tuning a search.

## What to look for: the scan type

No index, and the plan reads:

```
Limit (actual time=17.401..17.402 rows=10 loops=1)
  ->  Sort (actual time=17.400..17.401 rows=10 loops=1)
        Sort Method: top-N heapsort  Memory: 25kB
        ->  Seq Scan on items (actual time=0.026..16.845 rows=10000 loops=1)
Execution Time: 17.416 ms
```

`Seq Scan` (sequential scan) confirms every one of the 10,000 rows was
read and had its distance computed, then sorted, this is Lesson 10's
brute force, spelled out by the planner itself.

With an index built:

```
Limit (actual time=0.954..0.983 rows=10 loops=1)
  ->  Index Scan using items_embedding_idx on items (actual time=0.954..0.981 rows=10 loops=1)
Execution Time: 1.001 ms
```

`Index Scan using items_embedding_idx` confirms the index was actually
used, and there's no separate `Sort` step: an ANN index returns rows
*already* in approximate distance order, nothing left to sort.

## Why "confirms it was actually used" matters

Building an index doesn't guarantee Postgres's planner will choose it.
On a tiny table (like the six rows from the Beginner tier), a
sequential scan is often genuinely *faster* than using an index, so
the planner correctly ignores the index entirely. `EXPLAIN` is the only
reliable way to know which one actually happened for a given query,
guessing from wall-clock time alone can be misleading on small data.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/02_intermediate/14_explain_analyze_for_vector_queries/lesson.py
```

## Checkpoint

- **`EXPLAIN`**: the planner's predicted plan, doesn't execute the query.
- **`EXPLAIN ANALYZE`**: actually runs the query, reports real timings
  alongside the plan.
- **`Seq Scan`**: every row checked, brute force.
- **`Index Scan using <index name>`**: confirms a specific index was
  actually used, the only reliable way to know.

If anything here still feels unclear, ask before moving to Lesson 15.
