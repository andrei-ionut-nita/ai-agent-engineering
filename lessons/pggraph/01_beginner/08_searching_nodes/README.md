# Lesson 8: Finding a node by property, not by ID

## Where we left off

Every function so far started from a known ID: `p1`, `c1`. Real
callers usually don't have that, they have a name someone typed. This
lesson covers `graph.search()`, which finds nodes by property value
instead.

## `graph.search()`

```sql
SELECT node_table_name, node_id, node FROM graph.search(
  'name',
  'Alice',
  table_filter := 'public.people'::regclass,
  mode := 'exact'
);
```

The first two positional arguments are the property key and the value
to match, `name` has to be one of the columns you listed in
`graph.add_table()`'s `columns` array back in Lesson 3, pggraph can
only search what it was told to expose. `table_filter` narrows the
search to one node table; leave it unset and pggraph searches across
every registered table that has that column.

## `mode`: exact, contains, or prefix

`mode := 'exact'` requires a full match. `'contains'` does a substring
match (useful for "find anyone with 'bank' in their company name"),
`'prefix'` matches only from the start of the string. There's also
`case_sensitive` (default `true`) and `max_rows`/`row_offset` for
pagination, this is a real search endpoint, not a toy lookup, it's
meant to sit behind an actual search box.

## A note on performance at scale

`graph.search()` reads from the CSR-compiled node data pggraph already
holds in memory, it doesn't re-scan your Postgres table. For very large
node tables where `contains`/`prefix` matching needs to be fast even
before a graph build, the README's own example adds a plain Postgres
index:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX people_name_trgm_idx
  ON public.people USING gin (lower(name) gin_trgm_ops);
```

Not needed for a five-row example graph, worth knowing exists before
this course's later checkpoint projects grow the dataset.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/01_beginner/08_searching_nodes/lesson.py
```

## Expected output

```
Exact match for name='Alice':
  people  p1  {'id': 'p1', 'name': 'Alice', 'company_id': 'c1'}
```

## Checkpoint

- **`graph.search(key, value, table_filter, mode, case_sensitive, max_rows)`**:
  finds nodes by a registered property's value, not by ID.
- **only registered columns are searchable**: `columns := ARRAY['name']`
  in `graph.add_table()` is what makes `name` searchable at all.
- **`mode`**: `'exact'`, `'contains'`, or `'prefix'`; pair `'contains'`/`'prefix'`
  with a `pg_trgm`/`btree` index on large tables.

If anything here still feels unclear, ask before moving to Lesson 9.
