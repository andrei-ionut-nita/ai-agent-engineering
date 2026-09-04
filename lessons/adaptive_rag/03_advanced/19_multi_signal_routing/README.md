# Lesson 19: Where a Single Classifier-Then-Route Step Breaks Down

## Where we left off

Every routing decision since Lesson 3 has gone through the same shape:
send the question to Gemini, get back a label, route on the label. That's
accurate, but it costs one full model round trip for every question, no
matter how obviously simple that question is. "What oven setting does the
pizza dough recipe use?" needs exactly as much classification effort,
today, as a genuinely ambiguous, multi-part question does. At scale, that
flat cost is where a single classifier-then-route step starts to break
down: every question pays the same latency and the same API call, whether
it needs to or not.

## Three signals, no model call

```python
def complexity_score(query: str) -> float:
    length_signal = min(word_count(query) / 20, 1.0)
    density_signal = min(keyword_density(query) * 4, 1.0)
    entity_signal = min(entity_count(query) / 3, 1.0)
    return round(0.3 * length_signal + 0.4 * density_signal + 0.3 * entity_signal, 3)
```

Three cheap, purely local signals, combined with fixed weights, none of
them touching the network:

- **`word_count`**: a longer question is more likely to be doing more
  than one thing.
- **`keyword_density`**: the fraction of the question's words that come
  from a small list of multi-part or relational words (`and`, `both`,
  `compare`, `affect`, and so on). A question chaining two facts
  together tends to use one of these; a single-fact lookup usually
  doesn't.
- **`entity_count`**: a rough count of capitalized words that aren't the
  sentence's first word, a cheap stand-in for "how many distinct named
  things does this question mention."

None of these three signals is as reliable, on its own, as Lesson 3's
actual LLM classification. That's the honest tradeoff this lesson makes:
free and instant, in exchange for noisier labels.

## Running it

```bash
uv run python lessons/adaptive_rag/03_advanced/19_multi_signal_routing/lesson.py
```

## Expected output

Five questions, each scored and labeled without a single Gemini call:

```
Q: What oven setting does the pizza dough recipe use?
   words=9   density=0.00 entities=0  ->  score=0.135  label=simple_factual

Q: What two hobbies happen in the same room as the weather station?
   words=12  density=0.08 entities=0  ->  score=0.313  label=ambiguous
...
```

Notice the second question (genuinely multi-hop, per Lesson 4's own
example) scores as `ambiguous`, not `multi_hop`. That's not a bug, it's
the whole point of the next lesson: these three signals are cheap and
directional, not a replacement for Lesson 3's classifier on every
question, only on the clearly simple ones.

## Checkpoint

- Three purely local, zero-cost signals (length, keyword density, entity
  count) can approximate query complexity without a model call, but less
  precisely than an actual classification.
- A single classifier-then-route step breaks down at scale because it
  spends the same cost and latency on every question regardless of how
  obviously simple it is.
- This lesson doesn't replace Lesson 3's classifier, it sets up Lesson
  20's pre-filter: using these cheap signals only to catch the clear-cut
  simple cases, and falling through to the real classifier for anything
  the signals can't confidently place.

If anything here still feels unclear, ask before moving to Lesson 20.
