# Lesson 14: Swapping Redis in for LangGraph's graph-state persistence

## Where we left off

The langgraph course's own Lesson 24 (`Agent Memory (Checkpointer)`)
introduced `InMemorySaver`, LangGraph's default checkpointer: it
persists a graph's state between calls, but only for as long as the
process stays alive, restart it and every conversation's state is
gone. This lesson swaps in `RedisSaver`, from the
`langgraph-checkpoint-redis` package, everything about the graph stays
the same, only where its state lives changes.

## `RedisSaver`

```python
from langgraph.checkpoint.redis import RedisSaver

with RedisSaver.from_conn_string(dsn) as checkpointer:
    checkpointer.setup()
    graph = StateGraph(State)
    ...
    app = graph.compile(checkpointer=checkpointer)
```

`from_conn_string` takes the same kind of DSN every lesson in this
course already uses. `.setup()` creates whatever indexes `RedisSaver`
needs internally the first time it runs, safe to call every time, the
same idempotent-setup pattern as `CREATE EXTENSION IF NOT EXISTS` in
pgvector. Past this, `checkpointer=checkpointer` is the *only* line
that changes versus `InMemorySaver`, `graph.compile()`,
`app.invoke()`, everything else is ordinary LangGraph.

## Why this matters: state survives a restart

```python
config = {"configurable": {"thread_id": "user-42"}}
app.invoke({"count": 0}, config)
```

`thread_id` is how LangGraph tells checkpointers apart between separate
conversations, the same value across calls means "continue this
thread". With `InMemorySaver`, killing the Python process loses every
thread's state. With `RedisSaver`, the state lives in Redis, a new
process, given the same `thread_id`, picks up exactly where the last
one left off, `app.get_state(config)` proves it.

## Where this fits: working memory, not long-term memory

A graph's checkpoint (its current state, the messages so far, which
node runs next) is exactly the working-memory case from Lesson 12: it
needs to survive a restart *during* a conversation, but it's fine for
it to eventually expire once that conversation is truly over.
`RedisSaver` doesn't set a TTL on its own, a real system would add one
(`EXPIRE` on the underlying keys, or a periodic cleanup) the same way
Lesson 8's session hash got one.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/02_intermediate/14_redis_as_a_langgraph_checkpointer/lesson.py
```

## Expected output

```
First invoke (fresh state):  {'count': 1}
Second invoke (same thread): {'count': 6}
State after both calls:      {'count': 6}
```

## Checkpoint

- **`RedisSaver`**: a drop-in LangGraph checkpointer backed by Redis
  instead of memory, `from_conn_string` plus `.setup()`, then
  everything else about the graph is unchanged.
- **`thread_id`**: identifies which conversation's state a checkpointer
  call reads or writes.
- **survives a restart**: unlike `InMemorySaver`, a new process with
  the same `thread_id` picks up exactly where the last one left off.

If anything here still feels unclear, ask before moving to Lesson 15.
