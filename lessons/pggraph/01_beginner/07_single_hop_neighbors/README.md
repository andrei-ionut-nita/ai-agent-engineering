# Lesson 7: One hop out, with graph.get_neighbors()

## Where we left off

Lesson 6 fetched exactly one node. This lesson takes the first real
graph step: from a node, who (or what) is directly connected to it.

## `graph.get_neighbors()`

```sql
SELECT node_id, depth, node FROM graph.get_neighbors(
  graph_name := 'default',
  label := 'people',
  id := 'p1',
  direction := 'out',
  edge_types := ARRAY['works_at']
);
```

This is a single hop only, everything one edge away from `p1`, not a
multi-hop walk (that's `graph.traverse()`, next lesson). `edge_types`
restricts which relationship types to follow, useful once a graph has
more than one (Lesson 10 onward will). Leaving it unset would follow
every registered edge type.

## `direction`: which way to walk

`direction` takes exactly three values: `'out'`, `'in'`, or `'any'`,
not the more readable-looking `'outgoing'`/`'incoming'` you might guess
from the parameter name, pggraph is strict about this and errors if you
pass anything else. `'out'` follows the edge the way it was declared
(`people.company_id -> companies.id`), so from a person it reaches
their company. Because Lesson 4 registered `works_at` as
`bidirectional := true`, `'in'` from a *company* would also reach its
people, even though the foreign key itself only points one way.

## Reading the result

```
node_id=c1  depth=1  node={"id": "c1", "name": "Acme Bank"}
```

`depth` is always `1` for `get_neighbors()`, since it's single-hop by
definition, it's included because `graph.traverse()` returns rows in
the same shape with `depth` actually varying.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/01_beginner/07_single_hop_neighbors/lesson.py
```

## Expected output

```
Alice's direct neighbors (out, works_at):
  c1  depth=1  {'id': 'c1', 'name': 'Acme Bank'}
```

## Checkpoint

- **`graph.get_neighbors(graph_name, label, id, direction, edge_types)`**:
  one hop only, from a single starting node.
- **`direction`**: `'out'`, `'in'`, or `'any'`, not `'outgoing'`/`'incoming'`.
- **`edge_types`**: restricts which relationship types to follow; useful
  once a graph has more than one edge type registered.

If anything here still feels unclear, ask before moving to Lesson 8.
