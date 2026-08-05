# Lesson 22: Multi-tenant schemas, and the filtered-ANN-search trap

## Where we left off

Lesson 7 filtered vector search with a plain `WHERE category = ...`
clause, on six rows, with no index. This lesson scales that idea to a
real multi-tenant shape (many customers' data sharing one table), on a
large, indexed table, and runs into a genuinely surprising failure mode
along the way.

## The obvious schema: one shared table, a `tenant_id` column

```sql
CREATE TABLE items (
    id bigserial PRIMARY KEY,
    tenant_id text NOT NULL,
    embedding vector(256)
)
```

Simplest option, and usually the right starting point: one table,
filtered by `tenant_id` per query, exactly Lesson 7's pattern. It scales
well operationally (one schema to migrate, one index to maintain) as
long as no single tenant's traffic or data volume dominates the others.

## The trap: an ANN index searches globally, *then* filters

Build an `hnsw` index on that shared table and run a filtered search
for a tenant with very little data relative to the whole table:

```sql
SELECT id FROM items
WHERE tenant_id = 'small-tenant'
ORDER BY embedding <=> %s
LIMIT 5
```

You might reasonably expect this to always find that tenant's 5 closest
rows. Depending on the index and data, it can return **zero rows**,
even though 5 matching rows genuinely exist. `EXPLAIN ANALYZE` shows
why:

```
Index Scan using items_embedding_idx on items
  Filter: (tenant_id = 'small-tenant'::text)
  Rows Removed by Filter: 40
```

HNSW walks the graph toward the *closest vectors overall*, checking
roughly `ef_search` candidates (Lesson 12), and only *then* applies the
`WHERE` filter to whatever it found. If none of those closest-overall
candidates happen to belong to `small-tenant`, they all get filtered
out, and the query returns nothing, not because the data isn't there,
but because the ANN index never looked in the right neighborhood to
begin with.

## The planner's own safety net

Raise `ef_search` and re-run the same query, and it can come back
correct, but not always for the reason you'd expect. In this lesson's
data, `ef_search = 200` returns all 5 rows, and `EXPLAIN` reveals why:
the plan switched from `Index Scan` to a plain `Seq Scan`. Postgres's
query planner estimates the cost of both strategies before running a
query; a higher `ef_search` makes the ANN path look more expensive in
that estimate, and once it looks about as expensive as just scanning
the whole table (which is always exactly correct), the planner
switches to the one that's actually guaranteed to find every match.
Forcing the index path directly (`SET enable_seqscan = off`) and
raising `ef_search` all the way to its maximum (1000) still only
recovers 2 of the 5 rows here, the graph walk itself remains
approximate, no matter how wide. The real lesson: for a highly
selective filter on a shared table, trust the planner's own cost-based
judgment (verified with `EXPLAIN`, Lesson 14) over any single tuning
knob, and don't assume raising `ef_search` guarantees correctness by
itself.

## The structural fix: partition by tenant when one dominates

If a single tenant is consistently a tiny (or huge) sliver of a shared
table, raising `ef_search` per query is a band-aid, better to give
large or heavily-queried tenants their own table (or partition, Lesson
23) with its own index, so a search never has to wade through
irrelevant vectors from other tenants at all. Most systems land on a
hybrid: a shared table with a `tenant_id` column and a tuned
`ef_search` for the common case, with an escape hatch to split out a
tenant that's outgrown that model.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/03_advanced/22_schema_design_for_multi_tenant_vectors/lesson.py
```

## Checkpoint

- A shared table with a `tenant_id` column is the right default schema
  for multi-tenant vector data.
- ANN indexes filter *after* searching, a selective `WHERE` clause can
  cause a filtered search to return fewer rows than truly exist, or
  even zero.
- Postgres's planner can rescue this itself, by choosing a `Seq Scan`
  over the ANN index once the estimated cost makes that the safer bet,
  verify with `EXPLAIN`, don't assume.
- Giving a disproportionate tenant its own table or partition (Lesson
  23) is the structural fix when this keeps happening.

If anything here still feels unclear, ask before moving to Lesson 23.
