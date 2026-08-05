# Lesson 15: Bulk loading and upserting, measured, not assumed

## Where we left off

Every insert so far has used `executemany` (Lessons 4, 7-9) or a
per-row `COPY` (Lessons 10-14). This lesson does two things: times both
approaches honestly on the same data, and adds the other missing piece,
**upserting**, inserting a row or updating it in place if it already
exists, in one statement.

## Don't assume, benchmark

The common advice is "`COPY` is always fastest for bulk loads." Run
this lesson's first block and you may see the opposite: modern
`psycopg` (3.1+) already batches `executemany` into far fewer network
round trips than one-statement-per-row would need, a "pipeline" it
manages for you automatically. Row-by-row `cur.copy(...).write_row(...)`,
meanwhile, pays Python-level encoding overhead on every single row.

```python
with conn.cursor() as cur:
    cur.executemany("INSERT INTO items (embedding) VALUES (%s)", rows)
```

versus

```python
with conn.cursor() as cur, cur.copy("COPY items (embedding) FROM STDIN") as copy:
    for row in rows:
        copy.write_row(row)
```

`COPY` still earns its reputation in a different shape of job: loading
directly from an external file or stream, where Postgres reads a
continuous block of already-formatted data with no per-row Python
object construction at all (`psql`'s `\copy`, `pg_dump`/`pg_restore`,
and directly copying from a CSV file all work this way). The lesson
here isn't "always use X," it's: **time your actual workload, on your
actual driver version, before trusting a rule of thumb**, tooling
changes underneath advice like this faster than the advice gets
updated.

## Upserting: insert-or-update in one statement

```sql
INSERT INTO docs (external_id, content, embedding)
VALUES (%s, %s, %s)
ON CONFLICT (external_id) DO UPDATE
SET content = EXCLUDED.content, embedding = EXCLUDED.embedding
```

`ON CONFLICT (external_id)` names a column with a uniqueness constraint
(here, `external_id` as the primary key). If the insert would violate
it, Postgres runs the `DO UPDATE` instead, `EXCLUDED` refers to the row
that *would* have been inserted, letting you copy its columns into the
update. This is the real-world shape of syncing embeddings: re-running
an ingestion job over the same source documents should update existing
rows, not error out or create duplicates.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/02_intermediate/15_batch_inserts_and_upserts/lesson.py
```

## Checkpoint

- Benchmark bulk-insert strategies on your own driver and workload,
  don't assume `COPY` always wins, `psycopg`'s `executemany` pipelines
  automatically in recent versions.
- `COPY`'s real advantage is loading from an external file or stream
  with no per-row Python overhead.
- **upsert**: `INSERT ... ON CONFLICT (<unique column>) DO UPDATE SET
  ... = EXCLUDED. ...`, insert or update in one round trip.

If anything here still feels unclear, ask before moving to Lesson 16.
