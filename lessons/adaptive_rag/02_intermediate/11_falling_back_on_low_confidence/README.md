# Lesson 11: Falling Back on Low Confidence

## Where we left off

Lesson 10 gave the classifier a way to say "I'm not sure" alongside its
label, but saying it out loud didn't change anything yet, the router
still committed to whatever label came back, confident or not. This
lesson is where that number finally does something: below a threshold,
the label is no longer trusted enough to route on, and the router falls
back to a different, safer strategy instead.

## Picking a threshold without peeking at Lesson 17

`CONFIDENCE_THRESHOLD = 0.92` in this lesson's `lesson.py` comes from a
specific place: Lesson 10 measured a clean single-document question at
confidence 1.00, and a genuinely two-document question at 0.85-0.90
across repeated runs. The threshold sits just above the highest value
observed for the ambiguous case, a signal Lesson 10 already produced
on its own, before this course ever built a labeled evaluation set to
score anything against.

This matters because of what Lesson 17 does later: it reports a
precision@k score on a labeled question set. If this threshold had
instead been nudged until routing looked best on *that* same set,
the number Lesson 17 reports wouldn't measure anything real anymore,
it would just describe how well the threshold fits the questions it's
also being graded on. Tune against one signal (here, Lesson 10's own
examples), report against a different, held-out one (Lesson 17's set).
This is the same discipline `naive_rag` Lesson 14 uses for its
similarity threshold, tuned from Lesson 3's separate score-gap
observation, not from its own Lesson 17 evaluation set.

## The code, piece by piece

```python
def route_with_fallback(question: str, store: list[dict]) -> dict:
    label, confidence = classify_with_confidence(question)
    if confidence < CONFIDENCE_THRESHOLD:
        strategy, retrieved = "multi_hop (fallback)", multi_hop_retrieve(question, store)
    else:
        strategy, retrieved = route(label, question, store)
    ...
```

When confidence clears the threshold, `route()` does exactly what
Beginner Lesson 4 already did, dispatch by label. When it doesn't, the
label is set aside entirely and retrieval falls back to the wider
strategy, top-2 instead of top-1, on the reasoning that a question the
classifier is unsure about is exactly the kind where a narrow top-1
guess is most likely to miss.

## Running it

```bash
uv run python lessons/adaptive_rag/02_intermediate/11_falling_back_on_low_confidence/lesson.py
```

## Expected output

```
Q: What oven setting does the pizza dough recipe use?
  label: simple_factual (confidence=1.00)
  strategy used: naive
  sources retrieved: ['pizza-dough.md']

Q: How does wind speed affect things around the house?
  label: ambiguous (confidence=0.85)
  strategy used: multi_hop (fallback)
  sources retrieved: ['garden.md', 'weather-station.md']
```

The pizza question clears the threshold comfortably, naive top-1 runs
as routed and gets the one document that matters. The wind speed
question doesn't clear it, so the fallback overrides whatever label the
classifier picked and retrieves top-2 instead, and both `garden.md` and
`weather-station.md`, the two documents this question actually spans,
come back.

## Checkpoint

- A confidence threshold turns Lesson 10's number into an actual
  decision: below it, the label isn't trusted enough to route on.
- **Safe tuning**: pick the threshold from a signal separate from your
  final evaluation set (here, Lesson 10's own examples), never from the
  same set Lesson 17 reports a score against, that's the exact
  contamination this series keeps flagging.
- Falling back to a wider strategy doesn't fix a wrong label, it just
  hedges: retrieving more when uncertain is more likely to include the
  right document, at the cost of also including one that isn't needed.

If anything here still feels unclear, ask before moving to Lesson 12.
