# Lesson 15: `pydantic_evals` basics

## The `langsmith` equivalent, without leaving your codebase

The `langsmith` course built datasets and evaluators against a hosted
service: you uploaded examples, ran your chain against them, and read
results in the LangSmith UI. `pydantic_evals` is the same idea,
"define a set of inputs with expected outputs, run something against
them, score the results", but it runs entirely locally as a Python
library, no account or API key beyond Gemini's needed.

## `Case`, `Dataset`, and evaluators

A `Case` is one example: an input, and (optionally) the output you
expect.

```python
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import EqualsExpected

dataset = Dataset(
    name="capitals",
    cases=[
        Case(name="france", inputs="France", expected_output="Paris"),
        Case(name="japan", inputs="Japan", expected_output="Tokyo"),
    ],
    evaluators=[EqualsExpected()],
)
```

`EqualsExpected` is one of several built-in evaluators (others include
`Contains`, `IsInstance`, and `LLMJudge` for cases where "equals" is
too strict and you want a model to judge the answer instead). An
evaluator's job is always the same shape: look at a case's actual
output versus its `expected_output` (or whatever else it checks) and
produce a pass/fail or score.

## Running the dataset against your agent

`Dataset.evaluate_sync` takes any callable from input to output, here,
a thin wrapper around `agent.run_sync`, runs it against every case, and
prints a summary table:

```python
def ask_capital(country: str) -> str:
    return agent.run_sync(country).output

report = dataset.evaluate_sync(ask_capital)
```

The report shows one row per case (pass/fail per evaluator, duration)
and an averages row. This is the same "did my system regress" question
LangSmith's dataset runs answer, just rendered to your terminal instead
of a dashboard, which makes it something you can run as part of a test
suite, not just a manual check.

## Running it

```bash
uv run python lessons/pydantic_ai/02_intermediate/15_pydantic_evals_basics/lesson.py
```

## Checkpoint

- A `Case` is one input/expected-output example; a `Dataset` is a named
  collection of cases plus the evaluators to score them with.
- `evaluate_sync(task)` runs any input-to-output callable against every
  case and returns a report you can print or assert against.
- This is `pydantic_evals`'s answer to `langsmith`'s hosted datasets:
  same evaluation idea, but local, code-first, and runnable in CI.

If anything here still feels unclear, ask before moving to Lesson 16.
