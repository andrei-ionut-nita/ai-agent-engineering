# Lesson 4: Registering edges from a foreign key

## Where we left off

Lesson 3 registered `companies` and `people` as node tables. Nodes
alone aren't a graph, pggraph still has no idea `people.company_id`
means anything. This lesson registers that foreign key as an edge, the
relationship every later lesson traverses.

## `graph.add_edge()`: turning a foreign key into a relationship

```sql
SELECT graph.add_edge(
  from_table := 'public.people'::regclass,
  from_column := 'company_id',
  to_table := 'public.companies'::regclass,
  to_column := 'id',
  label := 'works_at',
  bidirectional := true
);
```

`from_column` is the column on `from_table` that holds a foreign key
value, `to_column` is the column on `to_table` it points at. pggraph
reads that relationship directly off your existing schema, there's no
separate edge table to create or maintain by hand. `label` is the edge
type name you'll use later when traversing (`edge_types := ARRAY['works_at']`),
pick something that reads like a relationship, not a table name.

## `bidirectional`: can you walk the edge both ways?

A foreign key is directional in the database (a person points at their
company, not the reverse), but the *relationship* it represents is
often meaningful in both directions: "who works at Acme Bank?" is just
as valid a question as "where does Alice work?". Setting
`bidirectional := true` tells the traversal engine it can walk this
edge from either end. Set it to `false` when the relationship really is
one-way, you'll see an example in Lesson 10's `reports_to` edge, where
walking from manager to report means something different than the
reverse.

## Checking what's registered

```sql
SELECT * FROM graph.registered_edges();
```

Like `graph.add_table()`, this is metadata: pggraph now knows the
*shape* of the relationship, but nothing has been compiled into a
traversable graph yet. `graph.status()` still reports zero edges. That
compilation step, `graph.build()`, is next lesson.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/01_beginner/04_registering_edges/lesson.py
```

## Expected output

```
Registered edges:
  people.company_id -> companies.id  label=works_at  bidirectional=True
```

## Checkpoint

- **`graph.add_edge(from_table, from_column, to_table, to_column, label, bidirectional)`**:
  registers an existing foreign-key-shaped relationship as a traversable
  edge, no separate edge table needed.
- **`label`**: the edge type name used later to filter traversals
  (`edge_types := ARRAY['works_at']`).
- **`bidirectional`**: whether the traversal engine can walk the edge
  from either end, not just in the foreign key's own direction.

If anything here still feels unclear, ask before moving to Lesson 5.
