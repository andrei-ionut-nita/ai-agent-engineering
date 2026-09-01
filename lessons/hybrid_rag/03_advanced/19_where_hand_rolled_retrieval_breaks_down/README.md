# Lesson 19: Where Hand-Rolled Retrieval Breaks Down

## Where we left off

`naive_rag` Lesson 19 timed a hand-rolled dense linear scan as its
corpus grew. This course has two hand-rolled retrievers to worry about,
and they don't scale the same way. This lesson times both, side by
side, with a synthetic corpus (random vectors, random tokens, same idea
as `naive_rag` Lesson 19, real embedding calls for thousands of
documents would be slow and pointless here).

## The code, piece by piece

```python
def idf(term, documents) -> float:
    doc_count = sum(1 for doc in documents if term in doc)
    return math.log(...)
```

Every call to `idf()` rescans the *entire* document collection to count
how many documents contain this one term, exactly as it's been written
since Lesson 4. That was fine at six documents. It stops being fine once
`sparse_hand_rolled()` calls it once per query term, per document being
scored, on every single search.

```python
for doc in documents:
    for term in query_tokens:
        ...
        score += idf(term, documents) * (...)
```

Two nested loops, and the inner one calls a function that's itself
another full scan of `documents`. That's the shape that gets expensive
fast, not because BM25 the algorithm is slow, but because this
particular hand-rolled implementation never caches anything.

## Running it

```bash
uv run python lessons/hybrid_rag/03_advanced/19_where_hand_rolled_retrieval_breaks_down/lesson.py
```

## Expected output

```
 documents   dense (s)  sparse (s)
         5      0.0002      0.0001
       500      0.0225      0.1533
     2,000      0.0835      2.6179
     5,000      0.2120     16.8829
```

Dense grows roughly linearly with corpus size, as expected for a linear
scan. Sparse grows far faster, by 5,000 documents it's nearly 80 times
slower than dense on the same corpus. That gap isn't inherent to BM25,
`rank_bm25` (Lesson 20) precomputes document frequencies once, up front,
and reuses them for every query afterward. It's specific to this
course's hand-rolled version, which was written for clarity in Lessons
3-5, one function per idea, not for repeated, cached lookups.

## Checkpoint

- This course's hand-rolled `idf()` rescans the whole corpus on every
  call, an O(n) operation that runs inside two nested loops, an
  unintentional near-quadratic cost that only shows up at scale.
- Dense linear scan and hand-rolled sparse both eventually need
  replacing, but sparse's hand-rolled version degrades faster, for a
  reason specific to *this* implementation, not to BM25 generally.
- Lesson 20 replaces the sparse half with `rank_bm25`, precomputed
  statistics instead of per-query rescans.

If anything here still feels unclear, ask before moving to Lesson 20.
