# Lesson 22: Alpha-Blended Fusion, Revisited

## Where we left off

Lesson 7 showed weighted-sum fusion's fragility with hand-rolled scores.
Now that both retrievers are real libraries (Lesson 21), this lesson
revisits alpha-blending one more time, and puts it head-to-head against
RRF on the same two queries, so the tradeoff is concrete rather than
abstract.

## The code, piece by piece

```python
distances = results["distances"][0]
dense_scores = {doc_id: 1 - distance for doc_id, distance in zip(ids, distances)}
```

`chromadb` returns *distance* (lower means closer), the opposite
convention from this course's own cosine similarity (higher means
closer). Flipping it with `1 - distance` isn't exact cosine similarity,
but it restores the "higher is better" direction min-max normalization
and blending both assume, the same care Lesson 10 took with score
conventions before combining anything.

```python
blended = sorted(names, key=lambda n: ALPHA * dense_norm[n] + (1 - ALPHA) * sparse_norm[n], reverse=True)
fused = reciprocal_rank_fusion([dense_ranking, sparse_ranking])
```

Both fusion methods run on the exact same two underlying rankings, so
this lesson isn't comparing different retrievers, only different ways of
combining the same two opinions.

## Running it

```bash
uv run python lessons/hybrid_rag/03_advanced/22_alpha_blended_fusion/lesson.py
```

## Expected output

```
Query: '20240115'
  alpha-blended (alpha=0.5) top-1: home_network.md
  RRF top-1:                       home_network.md

Query: "Why do vertical walls have ridges even though I didn't change any settings?"
  alpha-blended (alpha=0.5) top-1: 3d_printer.md
  RRF top-1:                       3d_printer.md
```

Both methods agree on both queries here, unsurprising given Lesson 7
already showed a wide range of `alpha` values recovers the right answer
on this course's corpus. The real distinction between them isn't
accuracy on easy cases, it's what each one requires to work correctly:
RRF needs nothing but rankings and never needs retuning as retrievers
change. Alpha-blending needs a normalization scheme chosen carefully per
retriever (this lesson's `1 - distance` conversion is exactly that kind
of retriever-specific detail RRF never has to think about) and a weight
that, per Lesson 7, still needs tuning against *something*.

## Checkpoint

- Alpha-blending works fine here, the same way it did in Lesson 7, once
  every retriever's score convention (similarity vs. distance) is
  handled correctly first.
- RRF and alpha-blending aren't "one is right," they're a genuine
  tradeoff: RRF costs you score information, alpha-blending costs you
  the complexity of normalizing and tuning correctly across retrievers
  that don't speak the same scale.
- This course defaults to RRF throughout for the reason Lesson 8 gave:
  fewer ways for a real system to get subtly wrong.

If anything here still feels unclear, ask before moving to Lesson 23.
