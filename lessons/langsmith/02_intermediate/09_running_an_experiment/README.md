# Lesson 9: Running the RAG app over a whole dataset at once

## What we're building

The same RAG app from Lesson 8, now run automatically against every
example in the `langsmith-course-rag-qa` dataset with a single call to
`evaluate()`, instead of invoking `rag_answer()` by hand once per
question.

## What this reveals

Lesson 8 built a dataset but only ran the app against one example
manually. `evaluate()` is the SDK's function for running your app
against an entire dataset in one call: it pulls every example, calls
your app once per example, and records every one of those runs together
under a single named **experiment**. An experiment is, in effect, a
snapshot: "here's exactly what this version of the app produced for
every example in the dataset, on this date."

This lesson deliberately runs `evaluate()` with no evaluators, only to
isolate what `evaluate()` itself does (iterate a dataset, call your app,
record an experiment) from what evaluators add on top (Lesson 10:
scoring each result automatically). Running an experiment and scoring it
are two separable ideas, even though in practice you'll almost always
do both at once.

## The code, piece by piece

```python
def target(inputs: dict) -> dict:
    return {"answer": rag_answer(inputs["question"])}
```

`evaluate()` doesn't know your app's real function signature,
`rag_answer(question: str) -> str`. `target()` is a small adapter: it
takes the example's `inputs` dict (`{"question": "..."}`, matching
Lesson 8's dataset shape), calls the real app, and returns an `outputs`
dict (`{"answer": "..."}`), also matching the dataset's shape so later
evaluators can compare like to like.

```python
results = evaluate(
    target,
    data=DATASET_NAME,
    experiment_prefix="rag-baseline",
    description="Baseline run of the RAG app, no evaluators yet.",
)
```

`data` names which dataset to pull examples from. `experiment_prefix`
becomes part of the experiment's name in the UI (a random suffix is
added so re-running doesn't collide with the previous run).
`evaluate()` blocks until every example has been run.

```python
for result in results:
    question = result["example"].inputs["question"]
    answer = result["run"].outputs["answer"]
```

The `results` object is iterable, one entry per example, each entry
carrying both the original `example` and the `run` your `target()`
function produced for it, so you can compare them programmatically
here, exactly what an evaluator does in Lesson 10.

## Running it

```bash
uv run python lessons/langsmith/02_intermediate/09_running_an_experiment/lesson.py
```

In the UI, open the `langsmith-course-rag-qa` dataset and find the new
experiment listed under it, named something like
`rag-baseline-<random-suffix>`. Open it to see all three questions and
the app's actual answers side by side.

## Checkpoint

- **Experiment**: one full run of your app over an entire dataset,
  recorded together and named, so it can be compared to other runs
  later.
- **`evaluate()`**: the SDK function that drives an experiment, calling
  your app once per dataset example.
- **`target()`**: the adapter function `evaluate()` calls per example,
  translating between the dataset's `inputs`/`outputs` shape and your
  app's real function signature.

If anything here still feels unclear, ask before moving to Lesson 10.
