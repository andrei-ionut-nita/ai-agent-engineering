# Lesson 11: `ivfflat`, pgvector's first index type

## Where we left off

Lesson 10 ran a brute-force search over 10,000 rows with no index. This
lesson builds pgvector's first ANN index type on that same data and
times the same query again.

## What "IVF" means

**IVFFlat** stands for "inverted file with flat compression." In plain
terms: at index-build time, pgvector groups all the vectors into
`lists` clusters (using k-means), each with a center point. A search
then does two things instead of one: find the handful of clusters
whose center is closest to the query, then only compute exact distance
against the vectors *inside* those clusters, skipping everything else
entirely.

```sql
CREATE INDEX ON items USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100)
```

`vector_cosine_ops` tells the index which distance operator to
optimize for, matching `<=>` from Lesson 5 (pgvector also has
`vector_l2_ops` for `<->` and `vector_ip_ops` for `<#>`, an index only
speeds up the operator it was built for). `lists = 100` is the number
of clusters; pgvector's own docs suggest starting around
`rows / 1000` for datasets up to a million rows, 100 for our 10,000
rows.

## `probes`: trading speed for recall at query time

```sql
SET ivfflat.probes = 10;
```

`probes` controls how many of those clusters get checked per search
(instead of just the single closest one). More probes means checking
more vectors, slower but higher recall; fewer probes means faster but a
higher chance of missing the true best match if it happened to land
in a cluster that wasn't checked. This is a *session* setting, tune it
per query without rebuilding the index.

## One real limitation: IVFFlat needs data before it's useful

An `ivfflat` index built on an empty (or nearly empty) table has no
meaningful clusters to build from; pgvector's docs recommend building
this index *after* loading your data, not before, unlike a typical
B-tree index you'd create up front. Rebuild it (`REINDEX` or drop and
recreate) if the table's contents change substantially later. Lesson
24 covers this maintenance question properly.

## A caveat about this lesson's data

Lesson 10's dataset is pure random noise, deliberately, so it's cheap
to generate and easy to reason about scale with. But random noise in
768 dimensions has essentially no real cluster structure, every point
is roughly equidistant from every other, which is close to the worst
case for a clustering-based index. You'll see `probes` need to go
surprisingly high here to recover the exact brute-force result. Real
embeddings are the opposite: they cluster tightly around actual topics
and meanings (that's the whole premise behind them working at all), so
in practice `ivfflat` recovers strong recall with far fewer probes than
this synthetic worst case needs.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/02_intermediate/11_ivfflat_index/lesson.py
```

## Checkpoint

- **IVFFlat**: clusters vectors into `lists` groups at build time; a
  search checks only `probes` of those clusters, not the whole table.
- **`vector_cosine_ops`**: tells the index which operator (`<=>`, `<->`,
  or `<#>`) it's optimized for.
- **`probes`**: a per-session query-time knob trading recall for speed.
- Build this index after loading data, not on an empty table.

If anything here still feels unclear, ask before moving to Lesson 12.
