# Lesson 26: More than one graph, and the "one graph per backend" rule

## Where we left off

Every function in this course has taken a `graph_name` argument
defaulting to `'default'`, without ever explaining why that's a
parameter at all. pggraph supports multiple, independent named graphs
in the same database, this lesson creates a second one and shows the
one real gotcha that comes with it.

## `graph.create_graph()`

```sql
SELECT graph_id, graph_name FROM graph.create_graph('archive');
SELECT graph_name FROM graph.list_graphs();
-- archive
-- default
```

A new graph is its own independent namespace: its own registered
tables and edges, its own build, its own node/edge counts, entirely
separate from `'default'`. A real use case is exactly what the name
suggests here, an `archive` graph over historical data, queried
occasionally, kept separate from a `default` graph over live data that
gets rebuilt often.

## `graph.set_current_graph()`, and the rule this lesson is really about

```sql
SELECT graph.set_current_graph('archive');
SELECT graph.add_table('public.companies'::regclass, id_column := 'id', columns := ARRAY['name']);
SELECT graph.build();
SELECT node_count FROM graph.status();  -- 5

SELECT graph.set_current_graph('default');
SELECT node_count FROM graph.status();  -- 0, not 11
```

Switching back to `'default'` doesn't restore its 11 nodes, `graph.status()`
reports `0` until you `graph.build()` again. This is a real constraint
worth internalizing: `graph.max_loaded_graphs_per_backend` defaults to
`1`, each Postgres backend (each connection) holds at most one
compiled graph in memory at a time. Switching graphs doesn't reload the
other one automatically, you rebuild (or, in a longer-lived
application, `graph.load_graph()` a previously persisted one) after
switching. In practice this means: pick one graph per connection/session
for the workload it's serving, don't design an application that expects
to freely interleave queries against two different named graphs on the
same connection.

## Tenancy, briefly

`graph.add_table()`'s `tenant_column` parameter and `graph.traverse()`'s
`tenant` argument exist for a related but different problem: many
tenants' data sharing *one* graph, scoped per query, rather than
separate graphs per tenant. That mechanism has its own session-level
configuration (`graph.tenant_setting`) and stricter validation than
this course has room to cover in depth, worth knowing it exists, a
`graph_name`-per-tenant split (this lesson's approach) is the simpler
starting point if you don't need query-level tenant isolation on a
shared graph.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/03_advanced/26_multi_graph_and_tenancy/lesson.py
```

## Expected output

```
default status: node_count=11, edge_count=16
Graphs after create_graph('archive'): ['archive', 'default']
archive status (after its own build): node_count=5, edge_count=0
default status, switched back, before rebuilding: node_count=0, edge_count=0
default status, after rebuilding: node_count=11, edge_count=16
```

## Checkpoint

- **`graph.create_graph(graph_name)`**: an independent namespace, own
  tables, edges, and build.
- **one loaded graph per backend**: switching graphs with
  `graph.set_current_graph()` doesn't keep the previous one's compiled
  state around, rebuild (or reload) after switching.
- **`tenant_column`/`tenant`**: a different mechanism, for sharing one
  graph across tenants with per-query scoping, briefly noted here, not
  covered in depth.

If anything here still feels unclear, ask before moving to Lesson 27.
