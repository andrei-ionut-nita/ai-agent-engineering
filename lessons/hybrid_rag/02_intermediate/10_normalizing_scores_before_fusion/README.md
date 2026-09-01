# Lesson 10: Normalizing Scores Before Fusion

## Where we left off

Lesson 8's RRF never looks at scores, only rank, and that's usually the
right default (Lesson 7 showed why picking a weight is fragile). But RRF
throws away real information: it can't tell "barely edged out the
runner-up" from "crushed the field," both are just "rank 1." Sometimes
that distinction matters, a reranking step, a confidence threshold
before answering at all, anything downstream that wants "how sure are
we," not just "what's the order." This lesson looks more closely at
*how* to normalize scores onto a comparable scale when you do need them,
picking up where Lesson 7's quick min-max pass left off.

## The code, piece by piece

```python
def min_max_normalize(scores: dict[str, float]) -> dict[str, float]:
    low, high = min(values), max(values)
    return {name: (score - low) / spread for name, score in scores.items()}
```

Lesson 7's approach: stretch the lowest score to `0`, the highest to
`1`, everything else proportionally in between. Simple, always lands in
`[0, 1]`, but sensitive to the shape of the distribution, see below.

```python
def z_score_normalize(scores: dict[str, float]) -> dict[str, float]:
    mean = statistics.mean(values)
    stdev = statistics.pstdev(values)
    return {name: (score - mean) / stdev for name, score in scores.items()}
```

A different question: not "where does this score fall between the min
and max," but "how many standard deviations from average is this
score." A document exactly average scores `0`, one far above average
scores well above `1`. This doesn't force anything into `[0, 1]`, the
scale is now "standard deviations," which needs its own handling before
mixing with a dense score.

## Running it

```bash
uv run python lessons/hybrid_rag/02_intermediate/10_normalizing_scores_before_fusion/lesson.py
```

## Expected output

```
document                 raw BM25    min-max    z-score
home_network.md             6.432      1.000      1.817
old_travel_router.md        4.158      0.646      0.834
espresso_machine.md         1.288      0.200     -0.405
3d_printer.md               1.233      0.192     -0.429
houseplants.md              0.245      0.038     -0.855
bike_maintenance.md         0.000      0.000     -0.961
```

Look at `old_travel_router.md`, the wrong document, still topically
close to the right one. Min-max puts it at `0.646`, nearly two-thirds of
the way to the winner's `1.000`, because min-max only knows "where does
this fall between the extremes I saw," not "how typical is this score."
Z-score puts the same document at `0.834`, meaningfully behind the
winner's `1.817` in standard-deviation terms, and clearly separated from
the genuinely irrelevant documents clustered near `-0.9`. Neither number
is "wrong," they're answering different questions, and which one a
downstream weighted blend should use depends on whether "relative
position" (min-max) or "how unusual is this" (z-score) is the thing that
actually matters for what happens next.

## Checkpoint

- **Min-max**: rescales to a fixed `[0, 1]` range, sensitive to outliers,
  a flat tail of near-ties gets stretched apart just because they're not
  the very minimum.
- **Z-score**: rescales relative to the mean and spread of the scores
  themselves, keeps the distribution's real shape, doesn't land in a
  fixed range.
- Both exist because RRF (Lesson 8) discards this information
  deliberately. When something downstream genuinely needs "how
  confident," not just "which rank," one of these is worth the
  complexity RRF avoids.

If anything here still feels unclear, ask before moving to Lesson 11.
