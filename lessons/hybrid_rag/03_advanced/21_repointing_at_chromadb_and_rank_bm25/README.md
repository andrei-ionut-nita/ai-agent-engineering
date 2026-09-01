# Lesson 21: Repointing at chromadb and rank_bm25

## Where we left off

Both halves of this course's hybrid pipeline now have a real-library
replacement, `chromadb` for dense (same as `naive_rag`'s Advanced tier)
and `rank_bm25` for sparse (Lesson 20). This lesson wires both in at
once, fused with the exact same RRF function from Lesson 8, unchanged.

## The code, piece by piece

```python
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="notes")
collection.add(ids=names, documents=texts, embeddings=vectors)
```

Same pattern as `naive_rag` Lesson 20: an ephemeral, in-memory
collection standing in for this course's own list-based dense store.

```python
dense_results = collection.query(query_embeddings=[query_vector], n_results=len(names))
dense_ranking = dense_results["ids"][0]
```

`n_results=len(names)` asks chromadb for *every* document, ranked, not
just a top-`k`. RRF needs a full ranking from each side to fuse
correctly, the same reason Lessons 6-18's hand-rolled dense and sparse
functions always returned complete rankings, not pre-truncated ones.

```python
fused = reciprocal_rank_fusion([dense_ranking, sparse_ranking])
```

Lesson 8's function, character-for-character unchanged. RRF never cared
whether a ranking came from a hand-rolled list or a real library, it
only ever needed a list of names in order, which is exactly what both
`chromadb` and `rank_bm25` hand back.

## Running it

```bash
uv run python lessons/hybrid_rag/03_advanced/21_repointing_at_chromadb_and_rank_bm25/lesson.py
```

## Expected output

```
Query: '20240115'
  dense (chromadb):  ['home_network.md', 'old_travel_router.md', '3d_printer.md', ...]
  sparse (rank_bm25): ['home_network.md', '3d_printer.md', 'bike_maintenance.md', ...]
  fused (RRF):        ['home_network.md', '3d_printer.md', 'bike_maintenance.md', ...]

Query: "Why do vertical walls have ridges even though I didn't change any settings?"
  dense (chromadb):  ['3d_printer.md', 'home_network.md', 'bike_maintenance.md', ...]
  sparse (rank_bm25): ['home_network.md', '3d_printer.md', 'houseplants.md', ...]
  fused (RRF):        ['3d_printer.md', 'home_network.md', 'bike_maintenance.md', ...]
```

Same behavior as every earlier lesson, real libraries underneath now.
The second query is the clearest proof RRF is doing real work here, not
just this course's hand-rolled version: `rank_bm25` alone puts the wrong
document (`home_network.md`) on top, and fusion still recovers the right
one (`3d_printer.md`), using `chromadb`'s ranking, exactly like Lesson 8
showed with hand-rolled scores.

## Checkpoint

- Both retrievers are now real libraries, `chromadb` (dense) and
  `rank_bm25` (sparse), the fusion logic connecting them (Lesson 8's RRF)
  needed zero changes.
- Requesting a *full* ranking (`n_results=len(names)`), not a
  pre-truncated top-`k`, from each retriever is what makes fusion
  possible at all.
- This is the shape a production hybrid retriever actually takes: two
  independent, well-tested libraries, one small fusion function gluing
  their outputs together.

If anything here still feels unclear, ask before moving to Lesson 22.
