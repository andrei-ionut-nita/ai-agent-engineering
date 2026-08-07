# Course index

A linear, one-concept-per-lesson path through **Redis**, the
in-memory store agents lean on for everything that needs to be fast
and short-lived: session state, conversation history, response
caching, rate limiting, and pub/sub streaming. Do these in order, top
to bottom, each lesson folder has a `README.md` (read first) and a
`lesson.py` (run second). Don't move to the next lesson until the
current one's checkpoint questions feel solid.

This course assumes you've done the [pgvector](../pgvector/) course,
which covers durable, queryable long-term storage for embeddings. This
course is deliberately the other half of that picture: Redis holds
the fast, ephemeral working memory an agent needs turn to turn (recent
messages, a cached answer, an in-flight rate-limit counter), while
pgvector holds what needs to survive and be searched by meaning over
the long run. Lesson 12 draws that line explicitly.

No AI model calls in this course, it's pure Redis and Python (plus
LangGraph in Lesson 14, with no LLM node in its graph). Lessons that
talk about "an LLM response" (Lesson 9) or "an agent" (Lessons 16, 19,
24) simulate the expensive call with a deliberately slow local
function, so nothing here needs a `GOOGLE_API_KEY`, the point is
Redis's own mechanics, not the model behind them. Lesson 17's vector
search uses a small, deterministic toy embedding for the same reason,
wiring in a real embedding model afterward is a one-line swap.

Setup: a local Redis, run via Docker Compose from the project root:

```bash
docker compose up -d
```

This starts a `redis-stack-server` instance on `localhost:6379`
(the "stack" image, not plain `redis`, because the advanced lessons on
vector and JSON search need the `RedisJSON` and `RediSearch` modules
it ships with), matching the `REDIS_DSN` in `.env.example`. Then, from
the project root:

```bash
uv run python lessons/redis/<tier>/<NN>_<name>/lesson.py
```

## Beginner: Redis as a place to hold fast, short-lived state

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_redis](01_beginner/01_what_is_redis/) | In-memory store, why agents need fast ephemeral state |
| 02 | [running_redis_via_docker_compose](01_beginner/02_running_redis_via_docker_compose/) | Bringing up `redis-stack-server` alongside pgvector/pggraph |
| 03 | [first_client_connection](01_beginner/03_first_client_connection/) | `redis-py`, `Redis.from_url()` |
| 04 | [strings_get_and_set](01_beginner/04_strings_get_and_set/) | The basic key/value type, `set`, `get` |
| 05 | [expiring_keys_with_ttl](01_beginner/05_expiring_keys_with_ttl/) | `setex`, `expire`, caching an LLM response for a while |
| 06 | [hashes_for_structured_data](01_beginner/06_hashes_for_structured_data/) | `hset`/`hgetall`, storing a session as a small object |
| 07 | [lists_for_conversation_history](01_beginner/07_lists_for_conversation_history/) | `rpush`/`lrange`, a chat message log |
| 08 | [beginner_checkpoint_project](01_beginner/08_beginner_checkpoint_project/) | **Checkpoint:** a chatbot with Redis-backed session memory |

## Intermediate: caching, rate limiting, and streaming for agents

| # | Lesson | Concept |
|---|--------|---------|
| 09 | [semantic_caching_llm_responses](02_intermediate/09_semantic_caching_llm_responses/) | Caching by prompt hash, cutting repeat API calls and cost |
| 10 | [rate_limiting_agent_calls](02_intermediate/10_rate_limiting_agent_calls/) | A token-bucket limiter with `INCR` and a TTL |
| 11 | [pub_sub_for_streaming_events](02_intermediate/11_pub_sub_for_streaming_events/) | `publish`/`subscribe`, streaming an agent's progress |
| 12 | [short_term_vs_long_term_memory](02_intermediate/12_short_term_vs_long_term_memory/) | Redis as working memory vs pgvector as long-term memory |
| 13 | [json_documents_with_redisjson](02_intermediate/13_json_documents_with_redisjson/) | Structured agent state beyond flat strings, via `RedisJSON` |
| 14 | [redis_as_a_langgraph_checkpointer](02_intermediate/14_redis_as_a_langgraph_checkpointer/) | Swapping Redis in for LangGraph's graph-state persistence |
| 15 | [task_queues_with_lists_and_streams](02_intermediate/15_task_queues_with_lists_and_streams/) | A simple work queue for handing tasks to worker agents |
| 16 | [intermediate_checkpoint_project](02_intermediate/16_intermediate_checkpoint_project/) | **Checkpoint:** a cached, rate-limited, streaming chatbot |

## Advanced: search, durability, and production concerns

| # | Lesson | Concept |
|---|--------|---------|
| 17 | [vector_search_with_redisearch](03_advanced/17_vector_search_with_redisearch/) | `RediSearch` vector indexes, Redis as a vector store |
| 18 | [hybrid_search_in_redis](03_advanced/18_hybrid_search_in_redis/) | Combining vector similarity with filters/full-text in one query |
| 19 | [redis_streams_for_multi_agent_queues](03_advanced/19_redis_streams_for_multi_agent_queues/) | Consumer groups, durable multi-agent task handoff |
| 20 | [persistence_rdb_vs_aof](03_advanced/20_persistence_rdb_vs_aof/) | Snapshotting vs append-only logging, durability tradeoffs |
| 21 | [production_and_cluster_basics](03_advanced/21_production_and_cluster_basics/) | Replication, sharding, and when a single node stops being enough |
| 22 | [security_auth_and_tls](03_advanced/22_security_auth_and_tls/) | `requirepass`, ACLs, TLS between an agent and its cache |
| 23 | [monitoring_and_memory_eviction](03_advanced/23_monitoring_and_memory_eviction/) | `INFO`, eviction policies, what happens when Redis runs out of RAM |
| 24 | [advanced_capstone_project](03_advanced/24_advanced_capstone_project/) | **Capstone:** a multi-agent system using Redis for memory, queue, and cache |
