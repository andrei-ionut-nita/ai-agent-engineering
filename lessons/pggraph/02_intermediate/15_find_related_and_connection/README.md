# Lesson 15: Starting from a search instead of a known ID

## Where we left off

Every traversal function so far started from a known `seed_id`. In
practice, you often start from a search term instead: "show me
everything related to whoever matches 'Alice'." `graph.find_related()`
and `graph.connection()` are the two functions built for that.

## `graph.find_related()`: search, then expand

```sql
SELECT node_table_name, node_id FROM graph.find_related(
  property_key := 'name', property_value := 'Alice',
  source_table := 'public.people'::regclass,
  max_depth := 2,
  target_table := 'public.people'::regclass
);
```

This is `graph.find()` and `graph.expand()` from Lesson 14, fused: it
searches for the starting node by property, then expands from whatever
it finds, in one call. Useful whenever the caller has a name, not an
ID, which in practice is most of the time.

## `graph.connection()`: two searches, one path between them

```sql
SELECT source_table_name, target_table_name, hop_count, readable_path
FROM graph.connection(
  source_key := 'name', source_value := 'Dan',
  target_key := 'name', target_value := 'Alice',
  source_table := 'public.people'::regclass,
  target_table := 'public.people'::regclass,
  max_depth := 4
);
```

Where `find_related` searches from one side, `connection` searches
*both* ends by property and finds the path between whatever it finds.
It returns the same step-by-step shape as `graph.shortest_path()`, plus
a `readable_path` column that renders the whole thing as one string:

```
people:p4 --works_at--> companies:c1 | companies:c1 --works_at--> people:p1
```

That's `graph.format_path()`'s formatting (Lesson 16 doesn't cover it
directly, but this is where you'd reach for it) applied automatically,
handy for logging or showing a path to an end user without writing your
own string-building loop.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/02_intermediate/15_find_related_and_connection/lesson.py
```

## Expected output

```
find_related('Alice', depth<=2):
  people  p2
  people  p4
connection(Dan -> Alice): people:p4 --works_at--> companies:c1 | companies:c1 --works_at--> people:p1
```

## Checkpoint

- **`graph.find_related()`**: search for a starting node by property,
  then expand from it, `find()` + `expand()` in one call.
- **`graph.connection()`**: search both endpoints by property, then find
  the path between them, `find()` + `shortest_path()` in one call.
- **`readable_path`**: a pre-formatted, human-readable rendering of a
  path, no manual string-building needed.

If anything here still feels unclear, ask before moving to Lesson 16.
