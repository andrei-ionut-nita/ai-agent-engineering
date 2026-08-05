# Lesson 23: Cypher, the same engine wearing different syntax

## Where we left off

Lessons 21-22 used GQL. Cypher (the query language Neo4j popularized,
and the one GQL itself was standardized from) is close enough in syntax
that pggraph exposes a Cypher-compatible entry point too, sharing the
same underlying planner.

## `graph.cypher()`

```sql
SELECT row FROM graph.cypher(
  'MATCH (p:people)-[:works_at]->(c:companies)
   RETURN p.name AS name, c.name AS company
   ORDER BY name
   LIMIT 20',
  hydrate := true
);
```

Nearly identical to Lesson 21's `graph.gql()` call, same `MATCH`
pattern, same `RETURN`, and in fact the same execution path
underneath, "overlapping patterns share IR" (intermediate
representation) is how the docs put it. If you already know Cypher
from Neo4j or another property graph database, this is the entry point
to reach for; if you're learning fresh, GQL and Cypher are similar
enough here that picking one is mostly a matter of which ecosystem
you're already in.

## `graph.cypher_compatibility()`: knowing the boundary

```sql
SELECT * FROM graph.cypher_compatibility();
```

This returns a table of Cypher features and whether pggraph supports
them: node and relationship pattern matching, `RETURN`/`WITH`/`ORDER
BY`/`LIMIT`, and mapped writes are supported; `CALL`/`YIELD`/`UNWIND`/
procedures and Cypher DDL (index/constraint/database statements) are
explicitly rejected, because those don't map to "a derived index over
PostgreSQL tables" the way pattern matching does. The last row says it
plainly: **`graph.cypher()` is a narrow compatibility surface, not a
full openCypher-compatible database API**. Worth checking this table
before assuming a Cypher query you know from elsewhere will just work.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/03_advanced/23_cypher_compatibility/lesson.py
```

## Expected output

```
People and their companies (via Cypher MATCH):
  Alice   Acme Bank
  Bob     Acme Bank
  Carol   Northwind Trading
  Dan     Acme Bank
  Eve     Acme Capital

Cypher compatibility:
  node MATCH                            supported
  single relationship MATCH             supported
  RETURN, WITH, ORDER BY, SKIP, LIMIT   supported
  mapped writes                         supported
  Cypher procedures and UNWIND          rejected
  Cypher DDL                            rejected
  Full openCypher compatibility         not claimed
```

## Checkpoint

- **`graph.cypher(query, params, hydrate)`**: same call shape as
  `graph.gql()`, sharing the same planner for overlapping syntax.
- **`graph.cypher_compatibility()`**: the definitive list of what's
  supported vs. rejected, check it before assuming a Cypher feature
  works.
- **not a full Cypher database**: no `CALL`/`UNWIND`/procedures, no
  Cypher-side DDL, PostgreSQL stays responsible for schema.

If anything here still feels unclear, ask before moving to Lesson 24.
