# Lesson 10: Writing evaluator functions that score each result

## What we're building

Two small evaluator functions, `keyword_overlap` (how many reference
words show up in the app's answer) and `is_concise` (whether the answer
stays under 25 words), run against every result in a new experiment
over the same RAG app and dataset from Lessons 8-9.

## What this reveals

Lesson 9's experiment recorded what the app produced, but nothing
judged whether that output was any good, you'd have had to read every
answer yourself. An **evaluator** automates that judgment: a plain
function that receives one result (the example's `inputs`, the app's
`outputs`, and the dataset's `reference_outputs`) and returns a score.

`evaluate()` accepts a list of evaluators, not just one, and runs every
one of them against every result. This matters because real quality
rarely reduces to a single number: `keyword_overlap` here measures
correctness-ish similarity to the reference, `is_concise` measures
something completely different (verbosity), and both show up as
separate, independently trackable metrics on the same experiment.

Note what these two evaluators are **not**: neither calls an LLM. They're
plain Python, cheap and deterministic. That's a legitimate, often
underrated evaluator style, useful whenever "correct" can be checked
mechanically. LLM-as-judge evaluators (an evaluator that itself calls a
model to grade subjective qualities like tone or helpfulness) are a
different, heavier tool for when a mechanical check isn't possible;
this course sticks to mechanical evaluators, the same shape generalizes
either way.

## The code, piece by piece

```python
def keyword_overlap(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    reference_words = set(reference_outputs["answer"].lower().split())
    answer_words = set(outputs["answer"].lower().split())
    overlap = reference_words & answer_words
    score = len(overlap) / len(reference_words) if reference_words else 0.0
    return {"key": "keyword_overlap", "score": round(score, 2)}
```

The three parameters are exactly what an evaluator function needs:
`inputs` (rarely used directly, but always available), `outputs` (from
`target()`), `reference_outputs` (from the dataset's `outputs`). The
return value's `"key"` names the metric, `"score"` is its value, either
can be a number or a boolean.

```python
def is_concise(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    word_count = len(outputs["answer"].split())
    return {"key": "is_concise", "score": word_count <= 25}
```

A boolean score is valid too, LangSmith shows it as a pass/fail rate
across the experiment rather than an average.

```python
results = evaluate(
    target,
    data=DATASET_NAME,
    evaluators=[keyword_overlap, is_concise],
    ...
)
```

The only change from Lesson 9: an `evaluators` list. `evaluate()` still
runs `target()` once per example exactly as before, then additionally
runs each evaluator against that example's result.

## Running it

```bash
uv run python lessons/langsmith/02_intermediate/10_custom_evaluators/lesson.py
```

In the UI, open the new experiment and look at its summary row, both
`keyword_overlap` and `is_concise` should appear as columns with a score
per example, plus an aggregate at the top.

## Checkpoint

- **Evaluator**: a function `(inputs, outputs, reference_outputs) ->
  {"key": ..., "score": ...}` that judges one result.
- **Multiple evaluators, one experiment**: `evaluate()` runs every
  evaluator you pass against every result, giving several independent
  metrics on the same run.
- **Mechanical vs. LLM-as-judge evaluators**: plain-Python checks are
  cheap and deterministic when "correct" can be checked mechanically;
  LLM-as-judge is a heavier alternative for subjective qualities.

If anything here still feels unclear, ask before moving to Lesson 11.
