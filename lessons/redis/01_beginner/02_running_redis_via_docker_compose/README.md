# Lesson 2: Bringing up `redis-stack-server` alongside pgvector/pggraph

## Where we left off

Lesson 1 ran `docker compose up -d redis` and connected to whatever
that started, without looking at the compose file itself. This lesson
slows down on that file, and on why this course's image isn't plain
`redis`.

## One compose file, three databases

This project's `docker-compose.yml` (project root) defines three
services: `db` (pgvector's Postgres), `graph_db` (pggraph's Postgres),
and `redis`. They're independent containers on independent ports, so
`docker compose up -d` with no service name would start all three at
once; `docker compose up -d redis` starts only the one this course
needs.

```yaml
redis:
  image: redis/redis-stack-server:7.4.0-v3
  restart: unless-stopped
  environment:
    REDIS_ARGS: "--requirepass ${REDIS_PASSWORD:-redis}"
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
```

`6379` is Redis's default port, unlike pgvector's Postgres (remapped to
`5433` to avoid clashing with a real Postgres install), there's rarely
already something else on `6379`, so no remapping is needed here.
`redis_data` is a named volume, the same durability-of-the-container
idea as `pgvector_data`: the container can be recreated without losing
what's stored, until you explicitly delete the volume.

## Why "stack", not plain `redis`

The official `redis` image ships only the core in-memory data
structures this tier covers (strings, hashes, lists). `redis-stack-server`
is the same core, plus modules bundled in: `RedisJSON` (Lesson 13) and
`RediSearch` (Lessons 17-18, vector and hybrid search). Using the stack
image from the start means Lesson 17 doesn't need a different
container, everything this course needs is already running.

## `REDIS_ARGS` and the password

`REDIS_ARGS` is how the stack image passes flags straight to the
underlying `redis-server` process, here `--requirepass`, setting a
password (`redis`, from `.env`'s `REDIS_PASSWORD`, defaulting to
`redis` if unset). A password on a local dev container mostly doesn't
matter for security, it's here so this course can honestly teach
`requirepass` in Lesson 22 against a server that already has it
configured, rather than turning it on later and breaking every earlier
lesson's connection string.

## Confirming the modules loaded

```python
r.execute_command("MODULE", "LIST")
```

`redis-py` has typed helpers for most commands (`.ping()`, `.get()`,
and so on), but not every admin command has one, `.execute_command()`
sends any command verbatim, the same escape hatch `psycopg`'s
`conn.execute()` provides for raw SQL. `MODULE LIST` returns every
module the running server has loaded; this lesson's output should
include `search` and `ReJSON` alongside Redis's own bundled modules.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/01_beginner/02_running_redis_via_docker_compose/lesson.py
```

## Checkpoint

- **the compose file**: three independent services (`db`, `graph_db`,
  `redis`), start only the one you need with `docker compose up -d
  <service>`.
- **`redis-stack-server`**: the same Redis core, plus `RedisJSON` and
  `RediSearch` bundled in, needed for Lessons 13, 17, and 18.
- **`MODULE LIST`**: confirms which modules a running server actually
  has loaded, via `execute_command` for commands without a typed
  `redis-py` method.

If anything here still feels unclear, ask before moving to Lesson 3.
