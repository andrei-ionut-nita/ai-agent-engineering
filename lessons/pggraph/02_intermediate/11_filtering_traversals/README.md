# Lesson 11: Filtering traversal results by node property

## Where we left off

Lesson 10 walked the `reports_to` chain unconditionally, every node
within range came back. Real questions are usually narrower: "who
within two hops has more than N years of seniority?" This lesson adds a
`filter` to `graph.traverse()`.

## Filter constructors, not raw SQL

pggraph's filters aren't a `WHERE` string you write by hand, they're
built from small JSONB-producing functions, then passed to `traverse`'s
`filter` parameter:

```sql
SELECT graph.gte('seniority_years', 5);
-- {"where": {"seniority_years": {"gte": 5}}}
```

`graph.eq`, `graph.gt`, `graph.gte`, `graph.lt`, `graph.lte`,
`graph.between`, `graph.in`, `graph.is_null` all follow the same shape,
and `graph.all(ARRAY[...])` combines several into one conjunctive
filter. This course only uses a handful; the full list is in the
project README's SQL API summary.

## Why a column needs `add_filter_column` first

Filtering only works on columns pggraph has been explicitly told to
index for it, `graph.add_filter_column('public.people'::regclass,
'seniority_years', 'numeric')`, which Lesson 10's setup already calls.
This is a separate step from `columns := ARRAY[...]` in
`graph.add_table()`, which controls what's *returned*, not what's
*filterable*. Filtering an unregistered column fails, this is
deliberate: filter columns get their own index structure at build time,
so pggraph wants you to opt in explicitly rather than pay that cost for
every column automatically.

## Filtering a traversal

```sql
SELECT depth, node_table_name, node_id FROM graph.traverse(
  seed_table := 'public.people'::regclass, seed_id := 'p1',
  max_depth := 2, edge_types := ARRAY['reports_to'], direction := 'in',
  filter := graph.gte('seniority_years', 5), hydrate := false
);
```

Starting from Alice and walking `reports_to` backward (who reports up
to her, direct or indirect), then keeping only people with 5+ years of
seniority. Bob (6 years) passes, Dan (2 years) doesn't, even though
he's within range.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/02_intermediate/11_filtering_traversals/lesson.py
```

## Expected output

```
Reports to Alice (any depth<=2) with seniority_years >= 5:
  depth=0  people  p1
  depth=1  people  p2
```

## Checkpoint

- **filters are built, not written**: `graph.gte(column, value)` and
  friends produce the JSONB `traverse()`'s `filter` parameter expects.
- **`graph.add_filter_column()`**: a column must be explicitly
  registered for filtering before a filter on it will work, separate
  from `add_table()`'s `columns` list.
- **`graph.all(ARRAY[...])`**: combines multiple filter conditions into
  one conjunctive filter, for when a single column check isn't enough.

If anything here still feels unclear, ask before moving to Lesson 12.
