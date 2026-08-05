# Lesson 12: `hnsw`, pgvector's graph-based index

## Where we left off

Lesson 11 built `ivfflat` and saw its honest weak spot: on data with no
real cluster structure, it needs a lot of probes to recover good
recall. This lesson builds pgvector's other index type, `hnsw`, on the
identical dataset, and it handles that same worst case noticeably
better.

## What "HNSW" means

**HNSW** stands for "hierarchical navigable small world." Instead of
clustering (IVFFlat's approach), it builds a multi-layer graph at
index-build time: every vector is a node, connected to its
approximate nearest neighbors, with a few sparse upper layers acting
like a highway system for jumping quickly to roughly the right
neighborhood before dropping down to the dense bottom layer to find the
true closest matches. A search walks that graph, following the edge
that gets closer to the query at each step, greedy hill-climbing rather
than checking whole pre-defined clusters.

```sql
CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64)
```

`m` is how many graph connections each node keeps (higher: better
recall and slower/larger index). `ef_construction` is how wide a
search the *build* process itself does while wiring up the graph
(higher: a better-built graph, slower to build).

## `ef_search`: the query-time knob

```sql
SET hnsw.ef_search = 40;
```

The HNSW equivalent of `ivfflat.probes`: how many candidates the search
keeps track of while walking the graph. Higher `ef_search` means
better recall, more computation per query.

## Why HNSW usually wins on real embeddings

Building the graph is slower than clustering (you'll see this directly
running it), but querying it is typically both faster *and* higher
recall than `ivfflat` at a comparable setting, because a graph walk
adapts to wherever the query actually lands, rather than committing to
a small, fixed set of pre-built clusters up front. This is why HNSW has
become the default recommendation for most new pgvector projects;
`ivfflat` remains useful when index build time or memory is the tighter
constraint.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/02_intermediate/12_hnsw_index/lesson.py
```

## Checkpoint

- **HNSW**: a multi-layer graph of approximate nearest-neighbor edges,
  searched by greedy hill-climbing rather than clustering.
- **`m`**, **`ef_construction`**: build-time knobs controlling graph
  connectivity and build quality.
- **`ef_search`**: the query-time recall/speed knob, HNSW's equivalent
  of `ivfflat.probes`.
- HNSW is typically the stronger default; `ivfflat` trades some of that
  quality for a faster, lighter build.

If anything here still feels unclear, ask before moving to Lesson 13.
