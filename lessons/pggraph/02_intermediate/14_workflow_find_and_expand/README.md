# Lesson 14: graph.find() and graph.expand(), the higher-level pair

## Where we left off

Everything so far has been a single, narrow function: search, or
traverse, or shortest-path. `graph.find()` and `graph.expand()` are a
step up in ambition, `find` is `search` with ranking and pagination
built in, `expand` is `traverse` with per-node filtering built in.
They're part of what the docs call the "workflow API," meant to sit
closer to an actual application endpoint.

## `graph.find()`

```sql
SELECT node_table_name, node_id, node FROM graph.find(
  'name', 'Alice',
  table_name := 'public.people'::regclass,
  mode := 'exact',
  max_rows := 20
);
```

If this looks nearly identical to `graph.search()` from Lesson 8,
that's because it is, same property/value/mode arguments, but `find()`
adds ranking (best matches first, for `'contains'`/`'prefix'` modes)
and standardizes on `max_rows`/`row_offset` pagination the way a real
search endpoint would expect.

## `graph.expand()`

```sql
SELECT depth, node_table_name, node_id, node FROM graph.expand(
  'public.people'::regclass, 'p1',
  max_depth := 2,
  edge_types := ARRAY['reports_to'],
  direction := 'in',
  target_table := 'public.people'::regclass,
  where_node := graph.gt('seniority_years', 3),
  include_start := false
);
```

`expand` is `traverse` plus `where_node`, a per-visited-node filter
using the same `graph.gt`/`graph.eq`/... constructors from Lesson 11,
plus a `target_table` to restrict which node type ends up in the
result. One thing worth being explicit about: **pass `direction`
explicitly** for a one-way edge like `reports_to`. This course found
`expand()`'s default (`'any'`) doesn't reliably walk a non-bidirectional
edge in reverse the way `get_neighbors()`'s `'any'` does, `direction :=
'in'` here is what actually reaches Alice's reports.

## Reading the result

Starting from Alice, walking `reports_to` in reverse (who reports up to
her), keeping only people with more than 3 years of seniority: Bob (6
years) passes, Dan (2 years) doesn't.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/02_intermediate/14_workflow_find_and_expand/lesson.py
```

## Expected output

```
find('Alice'): people p1 {'id': 'p1', 'name': 'Alice', 'company_id': 'c1', 'manager_id': None, 'seniority_years': 12}
expand(reports_to, in, seniority_years > 3):
  depth=1  people  p2
```

## Checkpoint

- **`graph.find()`**: `graph.search()` with ranking and pagination,
  meant to back a real search endpoint.
- **`graph.expand()`**: `graph.traverse()` with a `where_node` filter
  and a `target_table` restriction built in.
- **be explicit about `direction`**: on a one-way edge, don't rely on
  `expand()`'s default `'any'` to walk it in reverse.

If anything here still feels unclear, ask before moving to Lesson 15.
