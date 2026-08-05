# Lesson 16: Sampling a neighborhood's shape instead of listing it

## Where we left off

Every function so far returns individual nodes or a path. Sometimes you
don't want the full list, you want the *shape* of what's around a node:
how many companies, how many people, at each depth, without pulling
every single row back. That's `graph.neighborhood()`.

## `graph.neighborhood()`

```sql
SELECT depth, node_table_name, node_count, sample_nodes FROM graph.neighborhood(
  'name', 'Alice',
  source_table := 'public.people'::regclass,
  max_depth := 2,
  sample_k := 5
);
```

It starts the same way `find_related` did, a property search, then
traverses out. But instead of one row per node, it returns one row per
`(depth, node_table)` combination, with a *count* and a small *sample*
(capped at `sample_k`), not the full list. For a node with thousands of
neighbors, this is the difference between "here's a summary" and
"here's 3,000 rows you didn't ask for."

## Reading the result

```
depth=1  companies  node_count=1  sample_nodes=[{"id": "c1", "table": "companies"}]
depth=2  people     node_count=2  sample_nodes=[{"id": "p2", ...}, {"id": "p4", ...}]
```

One company at depth 1 (Alice's employer), two people at depth 2 (her
coworkers, reached by walking back out from that company). This is a
different shape of answer than everything else in this tier, worth
reaching for specifically when a caller (a UI, or an AI agent deciding
whether a neighborhood is worth exploring further) needs an overview
before committing to a full traversal.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/02_intermediate/16_neighborhood_sampling/lesson.py
```

## Expected output

```
Neighborhood of Alice (depth<=2, sample_k=5):
  depth=1  companies  node_count=1  sample=[{'id': 'c1', 'table': 'companies'}]
  depth=2  people     node_count=2  sample=[{'id': 'p2', 'table': 'people'}, {'id': 'p4', 'table': 'people'}]
```

## Checkpoint

- **`graph.neighborhood(property_key, property_value, source_table, max_depth, sample_k)`**:
  a summary of what's around a node, grouped by depth and table, not a
  full node listing.
- **`node_count` vs `sample_nodes`**: the true count at that depth, plus
  a capped sample, so a large neighborhood doesn't flood the result.
- **when to reach for it**: before a full traversal, when you (or an
  agent) need to know whether exploring further is worth it.

If anything here still feels unclear, ask before moving to Lesson 17.
