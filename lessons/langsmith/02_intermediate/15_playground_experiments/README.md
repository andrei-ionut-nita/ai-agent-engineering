# Lesson 15: Reading experiment results back into Python

## What we're building

The same RAG experiment from earlier lessons, run once more, then
pulled back down as a pandas `DataFrame` using `client.get_test_results`,
so its inputs, outputs, and scores can be inspected and analyzed
directly in Python instead of only through the UI's tables.

## What this reveals

LangSmith also has a **Playground**, a no-code part of the UI for
trying a different prompt or model against a dataset by hand, without
writing any Python. It's genuinely useful for quick, exploratory
iteration, but this course is code-first, so instead of a screenshot
walkthrough, this lesson covers the SDK-side equivalent of "getting
results out to look at them": pulling a finished experiment (whether it
came from `evaluate()`, as in every earlier lesson, or from the
Playground) back into a `DataFrame`.

This matters once you want to do something the UI's built-in views
don't offer directly: computing a custom aggregate, plotting a
distribution of scores, joining an experiment's results against some
other dataset you have locally, or just skimming everything in one
table without clicking into each row. `get_test_results` is the
function that gets you from "results live in LangSmith" to "results are
a normal Python object I can do anything with."

## The code, piece by piece

```python
results = evaluate(target, data=DATASET_NAME, evaluators=[keyword_overlap], experiment_prefix="rag-readback")
experiment_name = results.experiment_name
```

Nothing new, the same `evaluate()` call from Lesson 10, kept here so
this lesson is runnable on its own without depending on a previous
lesson having already created an experiment.

```python
dataframe = fetch_test_results_with_retry(experiment_name, "feedback.keyword_overlap")
```

Pulls the experiment named `experiment_name` back as a pandas
`DataFrame`, one row per example, with columns for every input field,
every output field, and every evaluator's score, all prefixed
(`input.`, `outputs.`, `feedback.`, note `input` is singular, `outputs`
is not) so they don't collide.

`evaluate()` returning doesn't mean the experiment (or, separately, its
per-run feedback scores) has finished writing on LangSmith's side yet.
Calling `get_test_results` immediately can raise, or come back missing
the feedback column you actually want. `fetch_test_results_with_retry`
retries with a short, growing wait until that specific column shows up,
an ordinary eventual-consistency gap you'll hit again anywhere a script
reads data it just finished writing, not something specific to this one
function.

```python
print(f"Average keyword_overlap: {dataframe['feedback.keyword_overlap'].mean():.2f}")
print(dataframe[["input.question", "outputs.answer", "feedback.keyword_overlap"]])
```

Ordinary pandas from here on, this experiment's results are just rows
and columns now, no different from data loaded from a CSV.

## Running it

```bash
uv run python lessons/langsmith/02_intermediate/15_playground_experiments/lesson.py
```

You should see the experiment's column names printed, the average
`keyword_overlap` score, and a small table of questions, answers, and
per-row scores, all computed locally from the pulled-down data.

## Checkpoint

- **Playground**: LangSmith's no-code UI for iterating on prompts
  against a dataset without writing Python, complementary to
  `evaluate()`, not a replacement for it.
- **`client.get_test_results(project_name=...)`**: pulls a finished
  experiment's full results back as a pandas `DataFrame`.
- **Why pull results back**: enables custom analysis, plotting, or
  joining against other data that the UI's built-in views don't cover.
- **Retry for eventual consistency**: data you just wrote (an
  experiment, its feedback scores) isn't guaranteed queryable the
  instant the write call returns, retry with a short growing wait
  rather than guessing a fixed delay.

If anything here still feels unclear, ask before moving to Lesson 16.
