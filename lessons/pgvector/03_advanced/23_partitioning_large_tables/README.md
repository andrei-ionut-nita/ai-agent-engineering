# Lesson 23: Declarative partitioning, the structural fix from Lesson 22

## Where we left off

Lesson 22 ended on a promise: when one tenant is a tiny (or huge) sliver
of a shared table, giving it its own partition avoids the
filtered-ANN-search trap entirely, rather than tuning `ef_search` and
hoping the planner falls back to a safe `Seq Scan`. This lesson builds
that partitioned table and proves it.

## Partitioning by `tenant_id`

```sql
CREATE TABLE partitioned_items (
    id bigserial,
    tenant_id text NOT NULL,
    embedding vector(256),
    PRIMARY KEY (tenant_id, id)
) PARTITION BY LIST (tenant_id);

CREATE TABLE partitioned_items_big PARTITION OF partitioned_items
    FOR VALUES IN ('big-tenant');
CREATE TABLE partitioned_items_small PARTITION OF partitioned_items
    FOR VALUES IN ('small-tenant');
```

`PARTITION BY LIST (tenant_id)` declares that this table is really
several physical tables under one logical name, split by the exact
value of `tenant_id`. Each `PARTITION OF` statement creates one of
those physical tables. To your application, and to every query written
so far, `partitioned_items` still looks like one ordinary table, insert
and select against it exactly as before, Postgres routes each row to
the correct partition automatically based on its `tenant_id`.

## One index declaration, one index per partition

```sql
CREATE INDEX ON partitioned_items USING hnsw (embedding vector_cosine_ops);
```

Run once against the parent table, and Postgres creates a matching
`hnsw` index on *each* partition individually, not one shared index
across all of them. `partitioned_items_big`'s index only ever sees
`big-tenant`'s vectors; `partitioned_items_small`'s index only ever
sees `small-tenant`'s. There's no more "the graph walk happened to
land in the wrong tenant's neighborhood," because there's no shared
graph to land in the wrong part of.

## Partition pruning: the query never touches the other tenant at all

```sql
SELECT id FROM partitioned_items
WHERE tenant_id = 'small-tenant'
ORDER BY embedding <=> %s
LIMIT 5
```

`EXPLAIN` on this query shows Postgres scanning only
`partitioned_items_small`, `big-tenant`'s 9,995 rows are never touched,
not filtered out after the fact (Lesson 22's problem), simply never
read in the first place. This is called **partition pruning**, and it's
the real payoff: Lesson 22's filtered search returned 0 of 5 correct
matches at the default settings; this one returns all 5, instantly,
every time.

## When this is worth the extra complexity

Partitioning adds real operational cost: more objects to manage, more
indexes to maintain, migrations that touch every partition instead of
one table. It earns that cost when a small number of tenants dominate
either the data volume or the query volume enough that Lesson 22's
shared-table-plus-`ef_search`-tuning approach keeps needing rescuing.
For the common case (many tenants, no one dominating), the shared table
from Lesson 22 remains the simpler, entirely reasonable default.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/03_advanced/23_partitioning_large_tables/lesson.py
```

## Checkpoint

- **`PARTITION BY LIST (...)`**: splits one logical table into several
  physical ones by an exact column value, transparent to ordinary
  queries.
- An index created on the parent table creates a separate, independent
  index per partition.
- **partition pruning**: a query naming a specific partition's key
  value never touches the other partitions' rows, structurally solving
  Lesson 22's filtered-search trap.

If anything here still feels unclear, ask before moving to Lesson 24.
