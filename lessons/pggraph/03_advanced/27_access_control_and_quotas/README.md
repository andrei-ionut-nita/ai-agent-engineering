# Lesson 27: Who can use a graph, and how much of it they can use

## Where we left off

Every lesson so far ran as the same Postgres role (`postgres`, this
course's Docker superuser) with unrestricted access. A graph shared
across a real application, or across multiple tenants, needs both
permission control (who can query or build it) and resource limits
(how much of it any one of them can consume). pggraph has its own
layer for both, separate from ordinary Postgres `GRANT`.

## `graph.grant_graph()`: permissions on the graph itself

```sql
SELECT graph_name, grantee, privilege FROM graph.grant_graph(
  'default', grantee := 'postgres', privilege := 'read'
);

SELECT * FROM graph.graph_privileges();
```

This is a permission model scoped to pggraph's own objects (graphs),
not Postgres tables, `privilege` is one of `read`/`write`/`build`/`admin`,
matching the kinds of operations this course has covered (querying,
GQL writes, `graph.build()`, and administrative calls like this one,
respectively). `graph.graph_privileges()` lists what's currently
granted, and `graph.revoke_graph()` (not run here, same shape in
reverse) removes it.

## `graph.set_graph_quota()`: limiting resource usage

```sql
SELECT scope_type, dimension, limit_value, enforcement
FROM graph.set_graph_quota(
  scope_type := 'cluster', dimension := 'max_named_graphs', limit_value := 10
);
```

Quotas are set per `scope_type` (`cluster`, `tenant`, `owner`,
`namespace`, or `graph`) and `dimension`, the *kind* of thing being
limited: `max_named_graphs`, `max_loaded_graphs_per_backend`,
`max_graph_jobs`, `max_artifact_storage_bytes`, not arbitrary text,
pggraph rejects a dimension it doesn't recognize. `enforcement :=
'hard'` (the default) actually blocks the operation once the limit is
hit; a soft mode would just flag it.

## `graph.graph_quota_usage()`: checking where you stand

```sql
SELECT scope_type, scope_key, dimension, limit_value, usage_value, exceeded
FROM graph.graph_quota_usage();
```

Reports every quota currently in effect (including ones nobody set
explicitly, like `owner`-scoped defaults) alongside actual usage and
whether it's `exceeded`. This is the function to check before an
operation that might hit a limit, the same "ask before you act"
instinct as `graph.sync_health()` from Lesson 25, applied to resource
limits instead of sync lag.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/03_advanced/27_access_control_and_quotas/lesson.py
```

## Expected output

```
Granted: default -> postgres (read)
Quota set: cluster / max_named_graphs, limit=10, enforcement=hard
Quota usage (max_named_graphs): [('cluster', 10, 1, False)]
```

## Checkpoint

- **`graph.grant_graph(graph_name, grantee, privilege)`**: pggraph's own
  permission model (`read`/`write`/`build`/`admin`), separate from
  ordinary Postgres `GRANT`.
- **`graph.set_graph_quota(scope_type, dimension, limit_value)`**:
  resource limits on a fixed set of recognized dimensions, not
  arbitrary metrics.
- **`graph.graph_quota_usage()`**: current usage vs. every active
  quota, worth checking before an operation that might hit one.

If anything here still feels unclear, ask before moving to Lesson 28.
