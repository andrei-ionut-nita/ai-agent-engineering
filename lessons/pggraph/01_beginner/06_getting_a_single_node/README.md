# Lesson 6: Looking up one node by its business ID

## Where we left off

Lesson 5 built the graph: 5 nodes, 6 directed edges, ready to query.
The simplest possible query is "give me this one node back", which is
what `graph.get_node()` does.

## `graph.get_node()`

```sql
SELECT * FROM graph.get_node(
  graph_name := 'default',
  label := 'people',
  id := 'p1',
  hydrate := true
);
```

`label` is the node table's name as registered in Lesson 3 (`people`),
`id` is the business ID from that table's `id_column` (`p1`, not an
internal pggraph identifier). `graph_name := 'default'` refers to the
graph you've been building all along, pggraph supports multiple named
graphs in one database (Lesson 26), and every function that takes a
`graph_name` defaults to `'default'` if you never created another one.

## `hydrate`: internal coordinates vs. real row data

The result includes a `node_idx`, pggraph's own internal array index
for this node inside the CSR structure, useful for nothing on its own.
The `node` column is what you actually want: the row's data as JSON,
built from the `columns` you listed in `graph.add_table()`. That JSON
is what `hydrate := true` produces, by reading the source table live.
Every traversal, search, and path function in this course has the same
`hydrate` option, and the same tradeoff: `true` costs an extra row
lookup per result but gives you real data back; `false` (used in
several later lessons) skips that lookup when you only need to know
*that* something is connected, not its full contents.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/01_beginner/06_getting_a_single_node/lesson.py
```

## Expected output

```
node_table_name=people  node_id=p1  node={'id': 'p1', 'name': 'Alice', 'company_id': 'c1'}
```

## Checkpoint

- **`graph.get_node(graph_name, label, id, hydrate)`**: looks up one
  node by its business ID, `label` is the registered table name.
- **`graph_name := 'default'`**: the graph built so far; pggraph
  supports multiple named graphs, `'default'` is the one used until
  Lesson 26.
- **`hydrate`**: `true` reads the real row from the source table and
  returns it as JSON; `false` skips that lookup when you only need
  coordinates, not data.

If anything here still feels unclear, ask before moving to Lesson 7.
