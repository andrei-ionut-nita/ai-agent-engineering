# Lesson 3: `redis-py`, and `Redis.from_url()` up close

## Where we left off

Lessons 1 and 2 already called `redis.Redis.from_url(dsn,
decode_responses=True)` without explaining it. This lesson slows down
on that line, the one every remaining lesson in this course starts
with.

## Why `redis-py`, and no wrapper around it

`redis-py` is the official Python client, maintained by Redis itself.
Like `psycopg` in the pgvector course, it's a thin layer: you call
methods that map almost one-to-one onto real Redis commands (`.get()`
sends `GET`, `.set()` sends `SET`), rather than an ORM-style
abstraction that hides which commands are actually running. Every
command this course covers is something you'll see directly.

## The DSN

```python
REDIS_DSN=redis://:redis@localhost:6379
```

Same shape as `POSTGRES_DSN`: a URL bundling everything needed to
reach a specific server. The pieces here: `redis://` (scheme), an empty
username before the `:` (Redis's default user has no name), `redis`
(the password, set by `requirepass` in Lesson 2's compose file),
`localhost:6379` (host and port). Redis has no separate "database name"
segment the way Postgres does, it has numbered databases (`0`-`15` by
default) instead, and every lesson in this course uses the default,
`0`, so it's simply omitted from the DSN.

## `Redis.from_url()`

```python
r = redis.Redis.from_url(dsn, decode_responses=True)
```

`from_url` parses the DSN and returns a client, no separate "connect"
step: `redis-py` opens (and pools, and reconnects) TCP connections
lazily, under the hood, as commands are actually sent. This is a real
difference from `psycopg.connect()`, which opens one connection
immediately and expects you to manage its lifetime with `with`.

## `decode_responses`, and why every lesson sets it

Redis itself has no concept of a Python string, everything it stores
and returns is bytes. Without `decode_responses=True`, `r.get("key")`
would hand back `b"value"`, not `"value"`, and every comparison and
f-string in this course would need an extra `.decode()`. Setting it
once, at connection time, makes the client behave the way you'd expect
from a Python API, and matches what every one of this course's lessons
assumes.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/01_beginner/03_first_client_connection/lesson.py
```

## Checkpoint

- **`redis-py`**: the official, thin Python client, methods map
  directly onto real Redis commands.
- **the DSN**: `redis://:<password>@<host>:<port>`, no database-name
  segment, this course always uses database `0`.
- **`decode_responses=True`**: without it, every value comes back as
  `bytes`, not `str`. Set once, at connection time.

If anything here still feels unclear, ask before moving to Lesson 4.
