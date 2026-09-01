# Lesson 19: Where Linear Scan Breaks Down

## Where we left off

Every retrieval lesson so far (Lesson 6 onward) has scored *every*
record in the store against the query, one at a time, then sorted and
sliced off the top `k`. That's a **linear scan**: exactly `N` similarity
computations for a store of `N` records, no shortcuts. At 5 records,
this is instant. This lesson asks: at what point does that stop being
true?

## Measuring it, not guessing it

Rather than reason abstractly about complexity, this lesson just times
the same `linear_scan` function this course has been using all along,
against stores of increasing size, using random vectors instead of real
embeddings (a real embedding call for 100,000 records would be slow and
expensive for a question this lesson doesn't need real meaning to
answer).

## The code, piece by piece

```python
def random_vector() -> list[float]:
    return [random.random() for _ in range(EMBEDDING_DIMENSIONS)]
```

A random vector has the same shape (768 floats) as a real Gemini
embedding, which is all this benchmark needs, cosine similarity doesn't
know or care whether a vector came from a real model or `random.random()`.

```python
def linear_scan(query_vector: list[float], vectors: list[list[float]]) -> float:
    start = time.perf_counter()
    scored = [cosine_similarity(query_vector, v) for v in vectors]
    scored.sort(reverse=True)
    return time.perf_counter() - start
```

The exact same shape as every `retrieve()` function since Lesson 6:
score every vector, then sort. `time.perf_counter()` before and after
measures how long that took, in seconds.

## Running it

```bash
uv run python lessons/naive_rag/03_advanced/19_where_linear_scan_breaks_down/lesson.py
```

## Expected output

```
      5 records: 0.0002s
  1,000 records: 0.0551s
 10,000 records: 0.5536s
100,000 records: 5.3432s
```

Exact numbers depend on your machine, but the pattern holds everywhere:
doubling the store size roughly doubles the search time. That's what
**linear scaling** means, and it's fine at hundreds or a few thousand
records (this course's entire fixture folder never gets remotely close),
but a system with millions of chunks, real production scale, would take
seconds per single query this way. That's the actual problem a real
vector database like `chromadb` (starting next lesson) or `pgvector`
(this repo's dedicated course) solves: not "storing vectors," which a
Python list already does fine, but searching them fast at scale using
indexing structures that avoid checking every single record.

## Checkpoint

- **linear scan**: comparing the query against every record, one at a
  time, the search strategy every lesson in this course has used so far.
- Its search time grows linearly with the number of records, fine for
  small stores, a real bottleneck at production scale.
- A vector database's main value isn't storage, it's an indexing
  structure that answers "what's most similar" without checking every
  record, the problem this course now turns to.

If anything here still feels unclear, ask before moving to Lesson 20.
