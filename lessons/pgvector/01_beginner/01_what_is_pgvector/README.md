# Lesson 1: What pgvector is, and why a database instead of memory

## Where we left off

The langchain course's Lesson 28 built an `InMemoryVectorStore`: embed
some chunks, hold them as a Python object, search them by meaning. It
worked, and it said so plainly: it's fine for learning and small
projects, but a production system with millions of documents would use
a dedicated vector database instead. This course is that dedicated
version, and it starts from a deliberately unglamorous fact: your
existing relational database can probably already do this.

## What pgvector actually is

**pgvector** is an extension to PostgreSQL, not a separate database.
Postgres already knows how to store integers, text, timestamps; the
`vector` extension teaches it one more column type, `vector(N)`, a
fixed-length list of floating point numbers, plus the operators needed
to measure distance between two of them. Once installed, a `vector`
column sits right next to your `text` and `timestamp` columns in the
same table, governed by the same transactions, backups, and permissions
as everything else.

That last part is the whole pitch. `InMemoryVectorStore` had no
persistence (restart your program, the embeddings are gone), no
transactions, and no way to `JOIN` a search result against the rest of
your data. A `vector` column in Postgres has all three, for free,
because it's still just Postgres.

## Getting Postgres with pgvector running

This course uses Docker Compose so setup is identical on every machine,
rather than asking you to install Postgres and compile an extension by
hand. From the project root:

```bash
docker compose up -d
```

`docker-compose.yml` runs the official `pgvector/pgvector` image (a
normal Postgres 17, with the extension already compiled in) and exposes
it on `localhost:5433` (not the default `5432`, in case you already have
a Postgres running for something else). `POSTGRES_DSN` in `.env`
already points at it.

## Turning the extension on

An extension being *installed* in the Postgres image isn't the same as
it being *enabled* in your specific database, that's one SQL statement:

```python
conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
```

`IF NOT EXISTS` makes this safe to run every time your program starts,
it's a no-op if some earlier run already enabled it. After this runs
once per database, `vector` is available as a column type in any table
you create there.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/01_beginner/01_what_is_pgvector/lesson.py
```

## Expected output

Something like this (the exact version numbers depend on the Docker
image and may differ slightly from below, that's fine):

```
Connected to Postgres 17.2 (Debian 17.2-1.pgdg120+1)
Extension 'vector' is enabled, version 0.8.0
```

If you get a connection error instead, Postgres probably isn't running
yet, see the
[Troubleshooting section](../../../../README.md#troubleshooting) in
this project's root README.

## Checkpoint

- **pgvector**: a Postgres extension adding a `vector(N)` column type
  and distance operators, not a separate database.
- **why a database, not memory**: persistence, transactions, and the
  ability to query vectors alongside your ordinary relational data.
- **`CREATE EXTENSION IF NOT EXISTS vector`**: turns the column type on
  for one database, safe to run repeatedly.

If anything here still feels unclear, ask before moving to Lesson 2.
