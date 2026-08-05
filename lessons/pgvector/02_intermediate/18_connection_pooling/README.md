# Lesson 18: Connection pooling, why a real app never opens one connection per query

## Where we left off

Every lesson so far opened one `psycopg.connect(...)`, did some work,
and closed it, fine for a short script that runs once. A real
application (a web server, an API) handles many requests concurrently,
and opening a brand-new Postgres connection for every single one of
them is expensive and doesn't scale.

## Why opening a connection is expensive

Connecting involves a TCP handshake, Postgres authenticating you, and
Postgres forking a new backend process to handle your session,
milliseconds of work that has nothing to do with your actual query.
Run the same trivial `SELECT 1` fifty times, opening a fresh connection
each time versus reusing a small pool of already-open ones, and the
difference is dramatic, connection setup, not query execution, is
almost the entire cost.

## `psycopg_pool`: a small set of connections, reused

```python
from psycopg_pool import ConnectionPool

pool = ConnectionPool(conninfo=dsn, min_size=2, max_size=10)
pool.wait()  # block until min_size connections are actually open

with pool.connection() as conn:
    conn.execute("SELECT 1")
```

`ConnectionPool` keeps `min_size` to `max_size` real connections open
in the background. `pool.connection()` hands you one already-open
connection from that set (blocking briefly if all of them are busy),
and returns it to the pool automatically when the `with` block ends,
instead of closing it. `pool.wait()` is optional, it just makes the
first benchmark below fair by not counting the pool's own warm-up time.

## Sizing a pool

`min_size` is how many connections stay open even when idle, ready
immediately. `max_size` is the ceiling, once every pooled connection is
busy, the next caller waits its turn rather than an unbounded number of
new connections being opened, protecting Postgres itself from being
overwhelmed by a traffic spike. A reasonable starting point is a
`max_size` on the order of your expected concurrent request count, not
your expected total request count, tuned against real load afterward.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/02_intermediate/18_connection_pooling/lesson.py
```

## Checkpoint

- Opening a Postgres connection costs a TCP handshake, authentication,
  and a new backend process, real time, unrelated to your query.
- **`ConnectionPool`**: keeps a small set of connections open and
  reuses them; `pool.connection()` borrows one, returns it
  automatically.
- **`min_size`** / **`max_size`**: how many connections stay warm, and
  the ceiling before new callers wait.

If anything here still feels unclear, ask before moving to Lesson 19.
