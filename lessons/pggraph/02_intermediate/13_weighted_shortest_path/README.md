# Lesson 13: Weighted paths, when hop count isn't the right measure

## Where we left off

`graph.shortest_path()` measures distance in hops, every edge costs the
same. That's wrong for a relationship like ownership, where a company
90%-owned by its parent and one 10%-owned aren't equally "close." This
lesson uses the `subsidiary_of` edge's `weight_column` (Lesson 10's
`ownership_pct`) with `graph.weighted_shortest_path()`.

## `graph.weighted_shortest_path()`

```sql
SELECT * FROM graph.weighted_shortest_path(
  'public.companies'::regclass, 'c4',
  'public.companies'::regclass, 'c1'
);
```

Same four required arguments as `graph.shortest_path()`, source and
target table/ID pairs. The difference is entirely in setup: because
`subsidiary_of` was registered with `weight_column := 'ownership_pct'`
back in Lesson 10, this function knows to sum that column along the
path instead of counting hops.

## Reading the result

Acme Wealth (`c4`) is 80%-owned by Acme Capital (`c3`), which is
100%-owned by Acme Bank (`c1`):

```
step=0  companies  c4  step_cost=0  total_cost=180
step=1  companies  c3  step_cost=80  total_cost=180  edge_weight=80
step=2  companies  c1  step_cost=180  total_cost=180  edge_weight=100
```

`step_cost` is the *cumulative* weight up to that step, `total_cost` is
the same final number repeated on every row, so you can read it off any
row without scanning to the end. `180` isn't a percentage here, it's
just the sum of the two edge weights, whether that sum means anything
domain-specific (like an effective ownership chain) is on you to
interpret, pggraph only adds up whatever numbers you put in
`weight_column`.

## What happens without a registered weight column

Calling this on an edge that was registered without `weight_column`
fails outright, unlike `graph.shortest_path()`, there's no implicit
"treat every edge as weight 1" fallback. Weighted paths are opt-in,
same as filter columns in Lesson 11.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/02_intermediate/13_weighted_shortest_path/lesson.py
```

## Expected output

```
Weighted shortest path, Acme Wealth -> Acme Bank (by ownership_pct):
  step=0  companies  c4  step_cost=0    total_cost=180
  step=1  companies  c3  step_cost=80   total_cost=180  edge_weight=80
  step=2  companies  c1  step_cost=180  total_cost=180  edge_weight=100
```

## Checkpoint

- **`graph.weighted_shortest_path(source_table, source_id, target_table, target_id)`**:
  same call shape as `shortest_path`, but sums a registered
  `weight_column` instead of counting hops.
- **weights are opt-in**: an edge needs `weight_column` set in
  `graph.add_edge()` (Lesson 10) before this function will work on it.
- **`step_cost` vs `total_cost`**: `step_cost` accumulates as you read
  down the rows, `total_cost` is the finished path's total repeated on
  every row.

If anything here still feels unclear, ask before moving to Lesson 14.
