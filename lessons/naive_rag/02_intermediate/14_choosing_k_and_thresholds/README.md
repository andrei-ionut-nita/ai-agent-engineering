# Lesson 14: Choosing k and Similarity Thresholds

## Where we left off

Lesson 8 asked "What is the capital of France?" against a document with
nothing to do with France, and top-k retrieval still returned its best
`k` chunks anyway, because top-k only ever asks "which of these is most
similar," never "is any of these similar *enough* to be worth using."
That gap is exactly what a **similarity threshold** closes.

## A threshold changes the question retrieval answers

Without a threshold, retrieval answers: "of everything I have, here are
the `k` closest matches." With a threshold, it answers a stricter
question: "of everything I have, here are the closest matches, *but
only the ones that clear this bar*." If nothing clears the bar, it can
correctly return nothing at all, rather than a false top match.

Where does the bar come from? Lesson 3's own experiment already
measured a real data point: an unrelated sentence scored roughly 0.50
against a related query on this same embedding model. `MIN_SCORE = 0.55`
in this lesson is chosen to sit just above that observed "unrelated"
baseline, not from a formula, there isn't a universal "good" cosine
similarity threshold, it depends on the embedding model and the specific
documents, and is usually tuned empirically like this.

## The code, piece by piece

```python
above_threshold = [record for record in scored if record["score"] >= min_score]
return above_threshold[:k]
```

The threshold filter runs *after* sorting by score, not instead of it:
first find the best matches available, in order, then drop whichever
ones don't clear `min_score`, then take up to `k` of what's left. Doing
it in the other order (filter first, then you'd lose the ranking) would
give you an arbitrary subset instead of the best available subset.

## Running it

```bash
uv run python lessons/naive_rag/02_intermediate/14_choosing_k_and_thresholds/lesson.py
```

## Expected output

```
Query: "What's the best way to get a crispy pizza crust?"
  Without threshold: 2 chunk(s) returned
    score=0.7xxx
    score=0.5xxx
  With threshold (min_score=0.55): 1 chunk(s) returned
    score=0.7xxx

Query: 'What is the capital of France?'
  Without threshold: 2 chunk(s) returned
    score=0.5xxx
    score=0.4xxx
  With threshold (min_score=0.55): 0 chunk(s) returned
```

The France query goes from "confidently returns two chunks that have
nothing to do with France" to "correctly returns nothing," a system
built around this can now check `if not retrieved: return "I don't have
information about that"` *before* even calling the model, saving an
API call and avoiding the risk of the model still blending in outside
knowledge despite the prompt instruction from Lesson 7.

## Checkpoint

- **similarity threshold**: a minimum score a retrieved chunk must clear
  to be used at all, letting retrieval honestly return "nothing
  relevant" instead of always returning `k` results.
- Thresholds are tuned empirically against your own embedding model and
  documents, not derived from a universal formula.
- Filter after ranking, not before, to make sure a threshold drops the
  worst matches specifically, not an arbitrary subset.

If anything here still feels unclear, ask before moving to Lesson 15.
