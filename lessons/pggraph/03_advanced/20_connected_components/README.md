# Lesson 20: Connected components, and finding what's isolated

## Where we left off

Every function so far started from a specific node. This lesson steps
back and asks a whole-graph question instead: how many separate,
disconnected pieces does this graph actually have, and is anything
sitting by itself with no relationships at all?

## `graph.component_stats()`: the whole-graph summary

```sql
SELECT * FROM graph.component_stats();
```

```
num_components=3  largest_component=8  num_isolated_nodes=1  total_active_nodes=11
```

Three separate pieces: Acme Bank's cluster (itself, its two
subsidiaries, and the people who work there or lead a project), Carol's
Northwind Trading (just her and her employer), and one company sitting
completely alone. This is the cheapest possible check for "is my graph
actually one connected thing, or several islands", useful as a sanity
check after a build, before trusting that a traversal from any node can
reach any other.

## `graph.components()`: the pieces, ranked by size

```sql
SELECT * FROM graph.components(max_rows := 20);
```

Returns each component's ID and size, largest first. This course's
example has three: size 8, size 2, size 1, the size-1 one is the
isolated company.

## `graph.isolated_nodes()`: nodes with zero edges

```sql
SELECT * FROM graph.isolated_nodes(max_rows := 100);
```

Specifically the nodes with *no* connections at all, not small
components, genuinely disconnected. In this course's data, that's Solo
Ventures (`c5`), a company registered as a node but never referenced by
any `works_at` or `subsidiary_of` relationship. In a real dataset, a
growing `isolated_nodes()` count over time is often a sign something
upstream stopped populating a foreign key it used to.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/03_advanced/20_connected_components/lesson.py
```

## Expected output

```
component_stats(): num_components=3, largest_component=8, num_isolated_nodes=1, total_active_nodes=11
components(): [8, 2, 1]
isolated_nodes(): [('c5', 'Solo Ventures')]
```

## Checkpoint

- **`graph.component_stats()`**: one-row whole-graph summary, cheapest
  way to check if a graph is fully connected.
- **`graph.components()`**: every component's size, ranked largest
  first.
- **`graph.isolated_nodes()`**: nodes with zero edges, worth monitoring
  as a data-quality signal over time.

If anything here still feels unclear, ask before moving to Lesson 21.
