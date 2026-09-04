# Lesson 8: End to End, Adaptive Q&A

## Where we left off

Lesson 7 proved routing earns its keep, comparing routed answers to
always-naive ones side by side. This lesson isn't about proving
anything new, it's about shape: one function, `answer()`, that wires
classify, route, and all three strategies together into the same clean
pipeline shape `naive_rag`'s own Lesson 8 used for its single strategy.
This is what the whole Beginner tier has been building toward.

## The whole pipeline, in one function

```python
def answer(query: str, store: list[dict]) -> dict:
    classification = classify(query)
    strategy = STRATEGIES[classification.label]
    result = strategy(query, store)
    return {"question": query, "label": classification.label, "answer": result}
```

Compare this to `naive_rag` Lesson 8's `ask()`:

```python
def ask(query: str, store: list[dict], k: int = 2) -> str:
    retrieved = retrieve(query, store, k)
    return generate_answer(query, retrieved)
```

Same shape, one extra step. `naive_rag`'s pipeline was retrieve, then
generate, always the same retrieve. This course's pipeline is classify,
then route (which itself retrieves and generates using whichever
strategy the label picked), then return. Everything before this lesson
built one of those two steps; this lesson is the two of them, together,
as one call.

## Why `answer()` returns the label too

`naive_rag`'s `ask()` returned just a string, the answer, because there
was only ever one strategy, there was nothing to disclose. This course's
`answer()` returns a small dict with the label included, because which
strategy handled a question is itself useful information, not an
implementation detail to hide. Printing which route each demo question
took is exactly what `main()` does below, and it's the same idea
`agentic_rag`'s later lessons build further (disclosing which tool was
called and why); here it's introduced at its simplest, one label per
answer.

## Running it

```bash
uv run python lessons/adaptive_rag/01_beginner/08_end_to_end_adaptive_qa/lesson.py
```

## Expected output

```
Q: How often does the wind sensor need re-oiling?
  route:  simple_factual
  answer: <every few months>

Q: What two hobbies happen in the same room as the weather station?
  route:  multi_hop
  answer: <names cello practice and the bookshelf, in the study>

Q: How does wind speed affect things around the house?
  route:  ambiguous
  answer: <combines the sensor's re-oiling need and the garden drying out>
```

Each question should take a different route, visibly printed before its
answer, that's the point of this lesson: one script, three strategies,
the right one picked automatically per question.

## Checkpoint

- **the whole pipeline**: `classify()` then `route()` is the entire
  Adaptive RAG architecture, once the three strategies and a vector
  store already exist, the same "few lines, everything else is
  refinement" shape every course in this series has closed its
  Beginner tier with.
- Returning which label handled a question, alongside the answer, makes
  the routing decision visible, not just an internal implementation
  detail.
- This is the version of Adaptive RAG the rest of this course tunes and
  hardens, not a toy that gets thrown away, same as every prior course's
  own end-to-end lesson.

If anything here still feels unclear, ask before moving to Lesson 9.
