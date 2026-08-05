# Lesson 13: Normalizing vectors, and why the metric choice matters

## Where we left off

Lesson 5 introduced `<->`, `<#>`, `<=>` and settled on `<=>` (cosine
distance) as this course's default, because that's what Gemini's
embeddings are trained for. This lesson shows *why* that choice
matters, with a small worked example where the three operators actually
disagree, then reconciles them.

## Where cosine and inner product can disagree

Cosine distance cares only about a vector's *direction*; inner product
(`<#>`) also cares about its *length*. That difference can flip a
ranking: a vector pointing in almost the exact same direction as the
query, but scaled down, can lose to a vector pointing somewhat further
off but scaled up, under raw inner product, while cosine correctly
prefers the one with the closer direction.

```python
query = [1.0, 0.0]
close_direction_small = [0.1, 0.0]   # same direction as query, tiny magnitude
off_direction_large = [0.9, 0.436]   # further off-direction, large magnitude
```

Lesson.py below inserts exactly these two toy vectors and ranks them
both ways, watch the order flip.

## Why this usually isn't a problem with real embeddings, but sometimes is

Embedding models are typically trained so that their outputs cluster
around roughly one magnitude, and Gemini's is no exception, run this
lesson's second block and you'll see every real chunk from `notes.txt`
comes back with almost the same vector length (roughly 0.58-0.59, not
the dramatic toy-example difference above). That's *why* `<#>` often
works fine in practice for a single embedding model's output. It stops
being safe the moment you mix vectors from different sources, different
models, differently truncated dimensions, or anything hand-constructed,
exactly the toy example above.

## Normalizing removes the ambiguity entirely

```python
import numpy as np
normalized = vector / np.linalg.norm(vector)
```

Once every vector has length exactly 1, cosine distance and (negative)
inner product become mathematically identical rankings, only their
absolute numbers differ. Some teams normalize at write time specifically
so they can use `<#>` (typically the cheapest of the three operators to
compute) with total confidence it agrees with cosine, without paying
for the extra normalization work at every single query. This course
keeps using `<=>` directly for simplicity, but knowing this trade exists
matters once query volume gets large.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/02_intermediate/13_choosing_a_distance_metric/lesson.py
```

## Checkpoint

- Cosine distance (`<=>`) compares direction only; inner product
  (`<#>`) also weighs magnitude, and the two can rank results
  differently.
- Real embeddings from one model are usually close enough in magnitude
  that this rarely bites, until vectors get mixed from different
  sources.
- Normalizing to unit length (`v / ||v||`) makes cosine and inner
  product rank identically, letting you safely use the cheaper operator.

If anything here still feels unclear, ask before moving to Lesson 14.
