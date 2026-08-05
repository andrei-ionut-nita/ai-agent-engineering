# Lesson 12: graph.shortest_path(), and a real limitation worth knowing

## Where we left off

Traversal (Lessons 10-11) answers "what's reachable, and how far?" A
different, equally common question is "what's the *shortest* way from
here to there?" That's `graph.shortest_path()`.

## `graph.shortest_path()`

```sql
SELECT step, node_table_name, node_id, edge_label FROM graph.shortest_path(
  'public.people'::regclass, 'p4',
  'public.people'::regclass, 'p1',
  hydrate := false
);
```

Four required positional arguments: source table, source ID, target
table, target ID. The result is the path itself, step by step, not just
a distance.

## What it actually returns, and why

Run the query above (Dan to Alice) and the path comes back through
`works_at`, not `reports_to`, even though this course has been building
toward a reporting-chain story:

```
step=0  people  p4
step=1  companies  c1  edge_label=works_at
step=2  people  p1  edge_label=works_at
```

Both paths (`p4 -reports_to-> p2 -reports_to-> p1`, and `p4 -works_at->
c1 -works_at-> p1`) are exactly two hops. `graph.shortest_path()`
searches across *every* registered edge type by default and returns
whichever shortest path it finds first, and unlike `graph.traverse()`,
**it takes no `edge_types` parameter to restrict that search**. If you
need a shortest path along one specific relationship only, you have two
options: temporarily work with a graph that only has that edge type
registered, or use `graph.traverse()` yourself and track the path by
hand. This is a real, current limitation of the function, not a
misunderstanding, worth knowing before you reach for it expecting
`graph.traverse()`'s filtering options.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/02_intermediate/12_shortest_path/lesson.py
```

## Expected output

```
Shortest path, Dan -> Alice:
  step=0  people     p4
  step=1  companies  c1  edge_label=works_at
  step=2  people     p1  edge_label=works_at
```

## Checkpoint

- **`graph.shortest_path(source_table, source_id, target_table, target_id, max_depth, hydrate)`**:
  returns the path itself, step by step, not just a hop count.
- **no `edge_types` filter**: unlike `graph.traverse()`, it searches
  every registered edge type and returns the first shortest match,
  which may not be the relationship you had in mind.
- **ties break toward registration order**, not toward any particular
  relationship being "more correct."

If anything here still feels unclear, ask before moving to Lesson 13.
