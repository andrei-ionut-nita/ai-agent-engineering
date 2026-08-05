# Course index

A linear, one-concept-per-lesson path through **pgvector**, the
Postgres extension that turns an ordinary relational database into a
place you can also store embeddings and search them by meaning. Do
these in order, top to bottom, each lesson folder has a `README.md`
(read first) and a `lesson.py` (run second). Don't move to the next
lesson until the current one's checkpoint questions feel solid.

This course assumes you've done Lessons 27-29 of the
[langchain](../langchain/) course, where `notes.txt` was loaded, split
into chunks, embedded, and searched with `InMemoryVectorStore`. That
lesson was honest about its own limit: it's fine for learning, but a
real system needs a vector store that survives a restart, scales past
memory, and can be queried with the rest of your ordinary relational
data. This course picks up exactly there and builds that dedicated,
production-shaped version, on Postgres.

Setup: a `GOOGLE_API_KEY` in a `.env` file at the project root (get a
free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)),
plus a local Postgres with pgvector, run via Docker Compose from the
project root:

```bash
docker compose up -d
```

This starts a `pgvector/pgvector` Postgres instance on `localhost:5433`
(port `5433`, not the default `5432`, to avoid clashing with any other
Postgres already running on your machine), matching the `POSTGRES_DSN`
in `.env.example`. Then, from the project root:

```bash
uv run python lessons/pgvector/<tier>/<NN>_<name>/lesson.py
```

## Beginner: Postgres as a place to store and search vectors

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_pgvector](01_beginner/01_what_is_pgvector/) | The `vector` extension, why a DB instead of in-memory |
| 02 | [connecting_with_psycopg](01_beginner/02_connecting_with_psycopg/) | `psycopg.connect`, cursors, plain SQL from Python |
| 03 | [vector_column_and_type](01_beginner/03_vector_column_and_type/) | `CREATE EXTENSION vector`, the `vector(N)` column type |
| 04 | [storing_real_embeddings](01_beginner/04_storing_real_embeddings/) | Inserting `GoogleGenerativeAIEmbeddings` output as rows |
| 05 | [distance_operators](01_beginner/05_distance_operators/) | `<->`, `<#>`, `<=>` — L2, inner product, cosine |
| 06 | [similarity_search_basics](01_beginner/06_similarity_search_basics/) | `ORDER BY ... LIMIT k` nearest-neighbor search |
| 07 | [filtering_with_metadata](01_beginner/07_filtering_with_metadata/) | Combining `WHERE` filters with vector search |
| 08 | [updating_and_deleting_vectors](01_beginner/08_updating_and_deleting_vectors/) | Keeping stored embeddings in sync with source data |
| 09 | [beginner_checkpoint_project](01_beginner/09_beginner_checkpoint_project/) | **Checkpoint:** Notes Semantic Search CLI |

## Intermediate: indexing, hybrid search, and talking to Postgres like an app would

| # | Lesson | Concept |
|---|--------|---------|
| 10 | [exact_vs_approximate_search](02_intermediate/10_exact_vs_approximate_search/) | Brute-force recall vs. approximate nearest neighbor |
| 11 | [ivfflat_index](02_intermediate/11_ivfflat_index/) | `CREATE INDEX ... USING ivfflat`, `lists`, `probes` |
| 12 | [hnsw_index](02_intermediate/12_hnsw_index/) | `USING hnsw`, `m`, `ef_construction`, `ef_search` |
| 13 | [choosing_a_distance_metric](02_intermediate/13_choosing_a_distance_metric/) | Normalizing vectors, cosine vs. L2 vs. dot product |
| 14 | [explain_analyze_for_vector_queries](02_intermediate/14_explain_analyze_for_vector_queries/) | Reading a query plan, confirming the index is used |
| 15 | [batch_inserts_and_upserts](02_intermediate/15_batch_inserts_and_upserts/) | `executemany`, `COPY`, `ON CONFLICT` upserts |
| 16 | [hybrid_search_text_and_vector](02_intermediate/16_hybrid_search_text_and_vector/) | `tsvector` full-text search combined with vector search |
| 17 | [reranking_results](02_intermediate/17_reranking_results/) | Merging and re-scoring two ranked result lists |
| 18 | [connection_pooling](02_intermediate/18_connection_pooling/) | `psycopg_pool`, why a real app never opens one connection per query |
| 19 | [intermediate_checkpoint_project](02_intermediate/19_intermediate_checkpoint_project/) | **Checkpoint:** Hybrid Search API |

## Advanced: production concerns, and closing the loop with LangChain

| # | Lesson | Concept |
|---|--------|---------|
| 20 | [langchain_pgvector_integration](03_advanced/20_langchain_pgvector_integration/) | `langchain-postgres`' `PGVector`, replacing `InMemoryVectorStore` |
| 21 | [persistent_rag_pipeline](03_advanced/21_persistent_rag_pipeline/) | A full RAG chain backed by a store that survives a restart |
| 22 | [schema_design_for_multi_tenant_vectors](03_advanced/22_schema_design_for_multi_tenant_vectors/) | `tenant_id` columns, indexing per-tenant vs. shared |
| 23 | [partitioning_large_tables](03_advanced/23_partitioning_large_tables/) | Declarative partitioning for tables that outgrow one index |
| 24 | [index_build_performance_and_maintenance](03_advanced/24_index_build_performance_and_maintenance/) | `maintenance_work_mem`, rebuilding indexes after bulk loads |
| 25 | [quantization_and_halfvec](03_advanced/25_quantization_and_halfvec/) | `halfvec`, trading precision for memory and speed |
| 26 | [monitoring_and_observability](03_advanced/26_monitoring_and_observability/) | `pg_stat_statements`, tracking real query latency |
| 27 | [migrations_and_reembedding_drift](03_advanced/27_migrations_and_reembedding_drift/) | What breaks when you upgrade your embedding model |
| 28 | [advanced_capstone_project](03_advanced/28_advanced_capstone_project/) | **Capstone:** a small FastAPI RAG service backed by pgvector |
