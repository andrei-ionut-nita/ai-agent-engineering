# Lesson 21: GQL, pattern-matching queries instead of function calls

## Where we left off

Every query so far has been a specific SQL function with specific
arguments, `traverse`, `shortest_path`, `search`. pggraph also
implements a subset of GQL (the ISO graph query language Cypher is
based on), letting you express the same kind of question as a
pattern to match, closer to how graph databases are usually queried.

## `graph.gql()`

```sql
SELECT row FROM graph.gql(
  'MATCH (p:people)-[:works_at]->(c:companies)
   WHERE c.name = $company
   RETURN p.id AS person_id, p.name AS name
   ORDER BY name',
  params := '{"company": "Acme Bank"}'::jsonb,
  hydrate := true
);
```

`MATCH (p:people)-[:works_at]->(c:companies)` reads almost like
English: match a `people` node, connected by a `works_at` edge, to a
`companies` node. `$company` is a bound parameter, passed separately
as `params` (a JSONB object), not string-interpolated into the query,
the same reason you'd use a parameterized query anywhere else. Every
row comes back as one JSONB value in a column literally called `row`,
shaped by whatever your `RETURN` clause named.

## Why this instead of `graph.traverse()`?

For a single hop with a property filter, GQL isn't obviously better
than the functions from earlier lessons, it's more a matter of taste
and what's easier to read for a given query. It starts to earn its
keep on multi-pattern queries, joining several relationships in one
`MATCH`, which would otherwise mean chaining several traversal calls
by hand. This course's capstone (Lesson 29) leans on it for exactly
that reason.

## What's supported, and what isn't

pggraph implements a *subset* of GQL: `MATCH`, `OPTIONAL MATCH`,
`WHERE`, `RETURN`, `ORDER BY`, `LIMIT`, aggregates (`count`, `sum`,
`avg`, `min`, `max`, `collect`), and (Lesson 22) write clauses. It is
not a general-purpose GQL engine, `graph.gql_explain(query)` shows you
the execution plan for a query without running it, useful for checking
whether pggraph understood your pattern the way you meant it before
you find out at runtime.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/03_advanced/21_gql_queries/lesson.py
```

## Expected output

```
People at Acme Bank (via GQL MATCH):
  p1  Alice
  p2  Bob
  p4  Dan
```

## Checkpoint

- **`graph.gql(query, params, hydrate)`**: pattern-matching queries,
  `$param` placeholders bound via a separate JSONB `params` argument.
- **`row`**: every result column comes back as one JSONB value per row,
  shaped by the query's `RETURN` clause.
- **`graph.gql_explain(query)`**: shows the plan without executing,
  useful for checking a pattern was understood as intended.

If anything here still feels unclear, ask before moving to Lesson 22.
