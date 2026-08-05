# Lesson 10: graph.traverse(), walking more than one hop

## Where we left off

Lesson 9's checkpoint chained two `graph.get_neighbors()` calls by hand
to walk two hops. `graph.traverse()` is the function that does that in
one call, for any number of hops, and it's the workhorse this whole
intermediate tier builds on.

## Growing the example: reporting structure and subsidiaries

This tier extends the running schema. `people` gains `manager_id` (a
self-referencing foreign key) and `seniority_years`; `companies` gains
`parent_company_id` and `ownership_pct`; a new `projects` table tracks
who leads what. Four edges now exist: `works_at` (unchanged),
`reports_to` (`people.manager_id -> people.id`, one-way, Dan reports to
Bob who reports to Alice), `subsidiary_of` (`companies.parent_company_id
-> companies.id`, one-way, weighted by `ownership_pct`), and `led_by`
(`projects.lead_person_id -> people.id`). Every lesson script in this
tier sets up this full schema itself, so each one still runs on its own.

## `graph.traverse()`

```sql
SELECT depth, node_table_name, node_id FROM graph.traverse(
  'public.people'::regclass, 'p4', 2,
  edge_types := ARRAY['reports_to'],
  direction := 'out',
  hydrate := false
);
```

The three required positional arguments are the seed table, seed ID,
and `max_depth`. Starting from Dan (`p4`) and following `reports_to`
outward two hops reaches Bob at depth 1, then Alice at depth 2, Dan's
manager's manager. `hydrate := false` skips reading the full row for
each result, useful here since only the chain of IDs matters, not the
row contents. This is what Lesson 9's two chained `get_neighbors()`
calls were really doing, one function call instead of writing the loop
yourself, and it works for any depth, not just two.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/02_intermediate/10_multi_hop_traversal/lesson.py
```

## Expected output

```
Reporting chain from Dan (out, reports_to, depth<=2):
  depth=0  people  p4
  depth=1  people  p2
  depth=2  people  p1
```

## Checkpoint

- **`graph.traverse(seed_table, seed_id, max_depth, edge_types, direction, hydrate)`**:
  a general multi-hop walk, the building block behind most of this
  tier's other functions.
- **the extended schema**: `reports_to` (one-way), `subsidiary_of`
  (one-way, weighted), and `led_by` join `works_at` in this tier's
  running example.
- **depth counts hops from the seed**, the seed itself is depth 0.

If anything here still feels unclear, ask before moving to Lesson 11.
