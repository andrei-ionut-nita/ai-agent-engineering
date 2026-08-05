# Course index

A linear, one-concept-per-lesson path through **pggraph**, the
PostgreSQL extension that compiles graph traversal, shortest-path, and
GQL/Cypher-style pattern matching directly on top of ordinary Postgres
tables. Do these in order, top to bottom, each lesson folder has a
`README.md` (read first) and a `lesson.py` (run second). Don't move to
the next lesson until the current one's checkpoint questions feel
solid.

This course pairs naturally with [pgvector](../pgvector/): both add a
new capability to an existing Postgres database instead of asking you
to run a separate specialized store, pgvector for similarity search,
pggraph for relationship traversal. They don't depend on each other,
either order works, together they cover the two things a relational
database doesn't do natively that an AI agent's memory usually needs.

Setup: a local Postgres with pggraph already installed, run via Docker
Compose from the project root:

```bash
docker compose up -d
```

This starts a second container (alongside pgvector's, if you've also
done that course) running the `ghcr.io/evokoa/pggraph` image on
`localhost:5434`, matching the `PGGRAPH_DSN` in `.env.example`. Its
database is named `graph`, not `ai_learning`, pggraph's own image
requires that name, see Lesson 2 for why. Then, from the project root:

```bash
uv run python lessons/pggraph/<tier>/<NN>_<name>/lesson.py
```

A note on the running example: this course builds up one shared
`companies`/`people` schema (extended in the intermediate tier with a
reporting chain, subsidiaries, and a projects table) across nearly
every lesson, and reuses the same Postgres database throughout, the way
a real application would. That means the schema grows forward as you
progress, it doesn't reset between lessons, running an early lesson
again after finishing a later tier may show a wider schema than that
lesson's own "Expected output" documents, that's expected, not a bug.
The capstone (Lesson 29) uses its own separately-named tables
specifically so it stays deterministic regardless of what you've run
before it.

## Beginner: registering tables, building a graph, and basic queries

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_pggraph](01_beginner/01_what_is_pggraph/) | The `graph` extension, why traversal belongs in Postgres |
| 02 | [installing_and_connecting](01_beginner/02_installing_and_connecting/) | The pggraph container, why its database must be named `graph` |
| 03 | [registering_tables_as_nodes](01_beginner/03_registering_tables_as_nodes/) | `graph.add_table()`, ordinary tables as node types |
| 04 | [registering_edges](01_beginner/04_registering_edges/) | `graph.add_edge()`, a foreign key as a traversable relationship |
| 05 | [building_the_graph](01_beginner/05_building_the_graph/) | `graph.build()`, compiling into an in-memory CSR structure |
| 06 | [getting_a_single_node](01_beginner/06_getting_a_single_node/) | `graph.get_node()`, business-ID lookup, `hydrate` |
| 07 | [single_hop_neighbors](01_beginner/07_single_hop_neighbors/) | `graph.get_neighbors()`, `direction := 'out'/'in'/'any'` |
| 08 | [searching_nodes](01_beginner/08_searching_nodes/) | `graph.search()`, property search, `mode` |
| 09 | [beginner_checkpoint_project](01_beginner/09_beginner_checkpoint_project/) | **Checkpoint:** Company Directory Explorer |

## Intermediate: multi-hop traversal, paths, filters, and staying in sync

| # | Lesson | Concept |
|---|--------|---------|
| 10 | [multi_hop_traversal](02_intermediate/10_multi_hop_traversal/) | `graph.traverse()`, `max_depth`, `edge_types` |
| 11 | [filtering_traversals](02_intermediate/11_filtering_traversals/) | `graph.gte()`/`graph.all()` filter constructors, `add_filter_column` |
| 12 | [shortest_path](02_intermediate/12_shortest_path/) | `graph.shortest_path()`, and its lack of an `edge_types` filter |
| 13 | [weighted_shortest_path](02_intermediate/13_weighted_shortest_path/) | `weight_column`, `graph.weighted_shortest_path()` |
| 14 | [workflow_find_and_expand](02_intermediate/14_workflow_find_and_expand/) | `graph.find()`, `graph.expand()`, `where_node` |
| 15 | [find_related_and_connection](02_intermediate/15_find_related_and_connection/) | `graph.find_related()`, `graph.connection()`, `readable_path` |
| 16 | [neighborhood_sampling](02_intermediate/16_neighborhood_sampling/) | `graph.neighborhood()`, counts + samples instead of full lists |
| 17 | [auto_discovery](02_intermediate/17_auto_discovery/) | `graph.preview_discover()`, why this course registers by hand |
| 18 | [incremental_sync](02_intermediate/18_incremental_sync/) | Sync overlays, `graph.apply_sync()`, `pending_sync_rows` |
| 19 | [intermediate_checkpoint_project](02_intermediate/19_intermediate_checkpoint_project/) | **Checkpoint:** Reporting Chain Finder |

## Advanced: GQL/Cypher, components, maintenance, and the capstone

| # | Lesson | Concept |
|---|--------|---------|
| 20 | [connected_components](03_advanced/20_connected_components/) | `graph.component_stats()`, `graph.isolated_nodes()` |
| 21 | [gql_queries](03_advanced/21_gql_queries/) | `graph.gql()`, `MATCH` pattern queries, `$params` |
| 22 | [gql_writes_and_mutable_overlay](03_advanced/22_gql_writes_and_mutable_overlay/) | `graph.mutable_enabled`, `'mutable_overlay'` build mode, `CREATE`/`SET` |
| 23 | [cypher_compatibility](03_advanced/23_cypher_compatibility/) | `graph.cypher()`, `graph.cypher_compatibility()` |
| 24 | [async_builds_and_maintenance](03_advanced/24_async_builds_and_maintenance/) | `graph.build_async_graph()`, `graph.vacuum()`, `graph.maintenance()` |
| 25 | [sync_policies_and_scheduled_jobs](03_advanced/25_sync_policies_and_scheduled_jobs/) | `graph.add_sync_policy()`, `graph.run_due_jobs()`, `graph.sync_health()` |
| 26 | [multi_graph_and_tenancy](03_advanced/26_multi_graph_and_tenancy/) | `graph.create_graph()`, one loaded graph per backend |
| 27 | [access_control_and_quotas](03_advanced/27_access_control_and_quotas/) | `graph.grant_graph()`, `graph.set_graph_quota()` |
| 28 | [monitoring_graph_health](03_advanced/28_monitoring_graph_health/) | `graph.status()` vs `resource_status()` vs `projection_status()` |
| 29 | [advanced_capstone_project](03_advanced/29_advanced_capstone_project/) | **Capstone:** a relationship-aware context API (FastAPI + pggraph) |
