# Lesson 12: Metadata-Aware Hybrid Retrieval

## Where we left off

Every lesson so far searched this course's entire six-document corpus.
A real corpus has thousands of documents, and a user often already knows
the scope they want, "just my network notes," "just this project."
This lesson adds that filter, applied identically to *both* retrievers
before they score anything, not after.

## The code, piece by piece

```python
CATEGORY = {
    "home_network.md": "network",
    "old_travel_router.md": "network",
    ...
}
```

One tag per document, the same idea as `naive_rag` Lesson 12's `source`
filter, a hand-assigned category instead of the filename itself.

```python
def hybrid_search(query, all_names, token_lists, doc_vectors, category=None):
    candidates = [n for n in all_names if category is None or CATEGORY[n] == category]
    dense = dense_ranking(query_vector, candidates, [doc_vectors[n] for n in candidates])
    sparse = sparse_ranking(query, candidates, [token_lists[n] for n in candidates])
    return reciprocal_rank_fusion([dense, sparse])
```

The filter happens once, before either retriever runs, both dense and
sparse only ever see the scoped-down candidate list. That's the whole
point of doing it here instead of filtering the fused result afterward:
an out-of-scope document can never sneak into the top-`k` through one
retriever just because it happened to fuse well, it's excluded from
scoring entirely.

## Running it

```bash
uv run python lessons/hybrid_rag/02_intermediate/12_metadata_aware_hybrid_retrieval/lesson.py
```

## Expected output

```
Query: 'Which build is the stable one?'
Plain hybrid search, all 6 documents: ['old_travel_router.md', 'home_network.md', '3d_printer.md', 'houseplants.md', 'bike_maintenance.md', 'espresso_machine.md']
Scoped to category='network' (2 documents): ['old_travel_router.md', 'home_network.md']
```

The top two results are identical whether searching all six documents
or just the two `network` ones, which is exactly what should happen,
filtering doesn't change the relative ranking of documents that were
already going to win, it removes everything else from contention. The
real benefit shows up at real scale: with thousands of documents instead
of six, that removal is what keeps an obviously out-of-scope document
from ever getting the chance to fuse its way into the top-`k` by
accident.

## Checkpoint

- Metadata filtering runs *before* retrieval, on the candidate set both
  retrievers score, not after fusion on the fused result.
- Applying the filter identically to both retrievers keeps their
  rankings comparable, one retriever seeing a different candidate pool
  than the other would make the fused ranking meaningless.
- On a small corpus, filtering mostly just confirms what unfiltered
  search already found. Its real value is precision at scale, keeping
  irrelevant categories out of contention entirely.

If anything here still feels unclear, ask before moving to Lesson 13.
