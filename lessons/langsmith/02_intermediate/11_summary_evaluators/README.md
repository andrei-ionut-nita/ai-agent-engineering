# Lesson 11: Scoring a whole experiment, not just one example at a time

## What we're building

One new evaluator, `pass_rate`, added alongside Lesson 10's
`keyword_overlap`, but of a different kind: it receives the entire
experiment's runs and examples at once, and produces a single
experiment-wide score instead of one score per example.

## What this reveals

Every evaluator in Lesson 10 ran once per example, in isolation, it
never saw the other examples' results. That's fine for "is this one
answer concise", but some questions can only be answered by looking at
the whole experiment together: "what fraction of examples passed some
threshold", "what's the worst score in this batch", "how does the
average compare to last week's run". A **summary evaluator** exists for
exactly this: instead of `(inputs, outputs, reference_outputs)` for one
example, it receives `runs` and `examples`, full lists covering every
example in the dataset, and returns one score for the whole experiment.

Per-example and summary evaluators aren't alternatives to choose
between, they answer different questions and are normally used
together, as here: `keyword_overlap` still tells you which specific
questions the app struggled with, `pass_rate` tells you, at a glance,
whether the app is "good enough" overall.

## The code, piece by piece

```python
def pass_rate(runs: list[Run], examples: list[Example]) -> dict:
    reference_by_id = {example.id: example.outputs["answer"] for example in examples}
    passed = 0
    for run in runs:
        reference = reference_by_id[run.reference_example_id]
        ...
        if overlap >= 0.5:
            passed += 1
    return {"key": "pass_rate", "score": passed / len(runs)}
```

`examples` is a list of `Example` objects (each has an `.id` and the
dataset's original `.outputs`), `runs` is a list of `Run` objects (each
has `.outputs`, what `target()` actually produced, and
`.reference_example_id`, which example it was run against). Matching
them up by id is how a summary evaluator connects "what happened" to
"what was expected" across the whole set. The return shape,
`{"key": ..., "score": ...}`, is identical to a per-example evaluator's,
just attached to the experiment as a whole instead of to one row.

```python
results = evaluate(
    target,
    data=DATASET_NAME,
    evaluators=[keyword_overlap],
    summary_evaluators=[pass_rate],
    ...
)
```

`evaluators` and `summary_evaluators` are separate lists on the same
call, `evaluate()` runs the per-example ones per result as before, then
runs each summary evaluator once, after every example has finished, over
the complete set of runs and examples.

## Running it

```bash
uv run python lessons/langsmith/02_intermediate/11_summary_evaluators/lesson.py
```

In the UI, open the new experiment. `keyword_overlap` appears as a
per-row column like before; `pass_rate` appears once, at the experiment
level, summarizing all three examples together.

## Checkpoint

- **Summary evaluator**: a function `(runs, examples) -> {"key": ...,
  "score": ...}` that scores an entire experiment at once, for
  aggregate questions a per-example evaluator can't answer.
- **`summary_evaluators` parameter**: passed to `evaluate()` alongside
  (not instead of) `evaluators`.
- **Matching runs to examples**: `run.reference_example_id` and
  `example.id` are how a summary evaluator connects each run back to
  the example it was run against.

If anything here still feels unclear, ask before moving to Lesson 12.
