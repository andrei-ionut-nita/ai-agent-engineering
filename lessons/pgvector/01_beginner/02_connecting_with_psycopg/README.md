# Lesson 2: Connecting with psycopg, cursors, and plain SQL

## Where we left off

Lesson 1 opened a connection and ran one statement. This lesson slows
down on the piece that every remaining lesson depends on: how
`psycopg` (the Python driver we're using to talk to Postgres) actually
executes SQL and hands results back.

## Why psycopg, and why no ORM

An ORM (object-relational mapper) like SQLAlchemy lets you write Python
classes instead of SQL, and translates your code into queries behind
the scenes. That's a reasonable choice for a large application, but it
adds a translation layer between you and what Postgres is actually
doing, which matters a lot in a course about a Postgres-specific
feature. `psycopg` is the plain, official Postgres driver: you write
real SQL strings, it sends them, you get rows back. Every `EXPLAIN`,
every index, every operator this course covers is something you'll see
directly, not through a layer that might paper over it.

## Connecting

```python
with psycopg.connect(dsn) as conn:
    ...
```

`psycopg.connect(dsn)` opens a network connection to Postgres, using a
DSN (data source name), a URL like
`postgresql://user:password@host:port/dbname` that bundles everything
needed to reach a specific database. Using `with` means the connection
closes automatically when the block ends, the same pattern as `with
open(...)` for files.

## Cursors: where a query actually runs

```python
with conn.cursor() as cur:
    cur.execute("SELECT 1 + 1")
    result = cur.fetchone()
```

A **cursor** is the object that actually sends a query and tracks its
results. `cur.execute(...)` sends the SQL. `cur.fetchone()` pulls back
one row (here, a single-element tuple, `(2,)`); `cur.fetchall()` would
pull back every row as a list of tuples.

`psycopg`'s connection object also has a shortcut, `conn.execute(...)`,
that creates a cursor for you and returns it, when you don't need to
keep the cursor around for multiple calls, as in Lesson 1. Both forms
appear across this course.

## Parameters: never build SQL with an f-string

```python
cur.execute("SELECT %s + %s", (2, 3))
```

The `%s` placeholders are filled in by `psycopg` itself, safely, no
matter what the values contain. Building a query with an f-string
instead, `f"SELECT {a} + {b}"`, is exactly how **SQL injection**
vulnerabilities happen: if `a` or `b` ever comes from a user, it could
contain SQL that changes what the query does. Every query in this
course passes parameters this way, never string-formatted in.

## Transactions and autocommit

By default, `psycopg` wraps every connection in an open transaction:
changes aren't visible to other connections (and can be undone with
`conn.rollback()`) until you call `conn.commit()`. For this course's
short, single-statement lessons, `psycopg.connect(dsn, autocommit=True)`
is simpler: each statement commits immediately, which is what Lesson 1
already used. Later lessons that need multiple statements to succeed or
fail together will use explicit transactions instead.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/01_beginner/02_connecting_with_psycopg/lesson.py
```

## Checkpoint

- **DSN**: a connection URL bundling user, password, host, port, and
  database name.
- **cursor**: the object that sends a query and holds its results;
  `conn.execute(...)` is a shortcut for a one-off cursor.
- **`%s` parameters**: always pass values this way, never f-string them
  into SQL, to avoid SQL injection.
- **autocommit**: each statement commits immediately, versus the
  default of an open transaction you commit or roll back yourself.

If anything here still feels unclear, ask before moving to Lesson 3.
