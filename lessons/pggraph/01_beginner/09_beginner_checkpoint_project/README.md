# Lesson 9: Checkpoint — Company Directory Explorer

## What this is

A small script that ties together everything from Lessons 1-8: build a
graph from `companies`/`people`, then answer two questions a real
directory tool would need to answer — "find this person" and "who else
works where they work" — using only pggraph functions, no hand-written
joins.

## What it does

`find_person(conn, name)` calls `graph.search()` to find a person by
name. `company_of(conn, person_id)` and `coworkers_of(conn, person_id,
company_id)` are two chained single-hop `graph.get_neighbors()` calls,
person to company, then company back out to everyone else there.
`main()` runs all three for `"Alice"` and prints the result as a small
directory entry.

## Where each piece came from

- Schema setup, table/edge registration, `graph.build()` — Lessons 3, 4, 5.
- `find_person()` — `graph.search()` from Lesson 8, with `mode := 'exact'`.
- `company_of()` — `graph.get_neighbors(direction := 'out')` from
  Lesson 7, person to company.
- `coworkers_of()` — the same function again, this time
  `direction := 'in'`, company back out to people, filtering the
  original person back out. Two single-hop calls chained by hand, this
  is exactly what `graph.traverse()` (Lesson 10) does in one call
  instead.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/01_beginner/09_beginner_checkpoint_project/lesson.py
```

## Expected output

```
Found: Alice (p1) at Acme Bank (c1)
Coworkers at Acme Bank:
  - Bob (p2)
```

## Try this yourself

- Change `find_person`'s query to `"Bob"` and confirm it returns Alice
  as the coworker instead.
- Search for `"Carol"` and confirm her coworker list comes back empty,
  she's the only person registered at Northwind Trading.
- Add a fourth person at Acme Bank in `setup_and_build()` and confirm
  `coworkers_of` picks them up without any code changes, since it reads
  the graph, not a hardcoded list.

If anything here still feels unclear, ask before moving to Lesson 10.
