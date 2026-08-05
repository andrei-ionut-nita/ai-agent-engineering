# Lesson 10: Exact search versus approximate nearest neighbor

## Where we left off

Every search in the Beginner tier ran `ORDER BY <distance> LIMIT k`
with no index. On six rows that's instant. This lesson uses a larger,
synthetic dataset (10,000 vectors) to show what that same query does
once "checking every row" is no longer free, and sets up why the next
two lessons add an index.

## Exact search: correct, but checks every row

With no index on the `embedding` column, `ORDER BY embedding <=> ...`
has exactly one way to run: compute the distance for *every* row, sort
all of them, take the top `k`. This is called a **sequential scan**
(you'll see it named that in `EXPLAIN`, next lesson). It is always
exactly correct, the true `k` closest vectors, every time, and its cost
grows linearly with the number of rows.

```python
t0 = time.perf_counter()
conn.execute("SELECT id FROM items ORDER BY embedding <=> %s LIMIT 10", (query,)).fetchall()
t1 = time.perf_counter()
```

On 10,000 rows of 768 dimensions each, this is still fast in absolute
terms (milliseconds), but "linear in the number of rows" is the whole
problem: at 10 million rows it's roughly a thousand times slower, and a
production system needs sub-second search regardless of table size.

## Approximate nearest neighbor: fast, occasionally not quite exact

An **ANN (approximate nearest neighbor) index** organizes vectors ahead
of time (at insert or build time) so a search only has to check a small
fraction of rows, not all of them, in exchange for a small chance of
missing the true single-best match in favor of an extremely close
second-best. That trade, "almost always exactly right, dramatically
faster," is the right one for the vast majority of real search use
cases, a user rarely notices or cares if result #7 and result #8 were
swapped.

**Recall** is the standard way to measure this: the fraction of the
true top-k that an approximate search actually returns. A recall of
0.98 means, on average, 98% of the true closest results show up; the
remaining 2% are replaced by results that were very nearly as close.
Lessons 11 and 12 build the two indexes pgvector offers (`ivfflat` and
`hnsw`) and let you tune this trade directly.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/02_intermediate/10_exact_vs_approximate_search/lesson.py
```

This creates a 10,000-row synthetic table (random vectors, since the
point here is scale, not meaning) with no index, times a brute-force
search, and prints it. Lesson 11 reuses this exact table and adds an
index to the same query.

## Checkpoint

- **sequential scan**: checking every row's distance, always exactly
  correct, cost grows linearly with row count.
- **ANN (approximate nearest neighbor) index**: pre-organizes vectors so
  a search checks only a fraction of rows, trading a small chance of
  imprecision for large speedups.
- **recall**: the fraction of the true top-k an approximate search
  actually returns.

If anything here still feels unclear, ask before moving to Lesson 11.
