# Lesson 1: What Redis is, and why agents need fast ephemeral state

## Where we left off

Every other course in this project stores something durable: LangGraph
checkpoints a graph's state, pgvector stores embeddings that need to
survive a restart, pggraph stores a whole relationship graph. This
course is about the opposite need: state that only has to live for a
few seconds or a few hours, and that has to be read and written *fast*,
because it sits directly in an agent's hot path, a session's message
history, a cached answer, a rate-limit counter checked on every call.

## What Redis actually is

**Redis** is an in-memory data store. "In-memory" is the whole pitch:
every read and write happens against RAM, not disk, so operations that
take milliseconds against a normal database take microseconds against
Redis. The tradeoff is durability, RAM loses its contents when the
process dies, so Redis is not, by default, the place you'd store
something you can never afford to lose (Lesson 20 covers how it can be
configured to persist anyway).

That tradeoff is exactly right for the kind of state an agent
accumulates turn to turn: the last ten messages of a conversation, a
counter tracking how many calls a user has made this minute, a cached
response to a prompt you've already answered once. None of that needs
to outlive a restart forever, all of it needs to be read back in under
a millisecond.

## Key-value, and more than key-value

At its simplest, Redis is a key-value store: a key is a string, a
value is... also usually a string, but not only. This course builds up
from `SET`/`GET` (Lesson 4) through hashes, lists, and later streams
and full-text/vector search, each one a different shape of value
addressed by the same kind of key. Every one of them keeps the same
property: fast, in-memory, simple commands.

## Getting Redis running

This course uses Docker Compose, same as pgvector and pggraph, so setup
is identical on every machine. From the project root:

```bash
docker compose up -d redis
```

Lesson 2 goes deeper on what's actually in that compose file. For now,
this starts a `redis-stack-server` instance on `localhost:6379`,
matching the `REDIS_DSN` in `.env`.

## Proving it's alive

```python
r.ping()
```

`PING` is Redis's own "are you there" command, `redis-py` (the client
library used throughout this course) exposes it as `.ping()`, returning
`True` once the round trip succeeds. It's the same first move as
`psycopg.connect` in pgvector: prove the connection works before
building anything on top of it.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/01_beginner/01_what_is_redis/lesson.py
```

## Expected output

Something like this (the exact version number depends on the Docker
image and may differ slightly, that's fine):

```
Connected to Redis 7.4.2
PING -> True
Used memory: 1.2M
```

## Checkpoint

- **Redis**: an in-memory data store, fast because everything happens
  in RAM instead of on disk, at the cost of durability by default.
- **why agents need it**: session state, caches, and counters that need
  to be read and written on every turn, where milliseconds matter.
- **`PING`**: the simplest possible "is the server up" check, exposed
  by `redis-py` as `.ping()`.

If anything here still feels unclear, ask before moving to Lesson 2.
