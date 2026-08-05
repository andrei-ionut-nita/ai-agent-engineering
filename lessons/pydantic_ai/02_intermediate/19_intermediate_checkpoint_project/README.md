# Lesson 19 (Checkpoint): A multi-agent support triage system, with evals

## What you're building

A support-ticket triage agent that delegates to one of two specialist
agents (billing, technical), each returning its own validated response
type, plus a `pydantic_evals` dataset that checks whether triage routes
messages correctly. This exercises the whole intermediate tier:

- **Multi-agent delegation** (Lesson 12): the triage agent's tools call
  `billing_agent` and `technical_agent` directly.
- **Structured output unions** (Lesson 16): the triage agent's
  `output_type` is `BillingResponse | TechnicalResponse`, whichever
  specialist actually handled it.
- **Usage passthrough** (Lesson 13): each delegated call passes
  `usage=ctx.usage` so the combined cost is visible on the outer
  result.
- **`pydantic_evals`** (Lesson 15): a small dataset of sample tickets
  with expected routing, scored with a custom evaluator.

## A custom evaluator

Lesson 15 used a built-in evaluator (`EqualsExpected`). Here, the check
is "did triage route to the right specialist", which needs a small
custom one, a plain dataclass subclassing `Evaluator`:

```python
from dataclasses import dataclass
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

@dataclass
class MatchesKind(Evaluator):
    def evaluate(self, ctx: EvaluatorContext) -> bool:
        return ctx.output == ctx.expected_output
```

`ctx.output` here is whatever the task function returns for a case
(this lesson's task returns just the `.kind` string, "billing" or
"technical", to keep the comparison simple); `ctx.expected_output` is
the `Case`'s `expected_output`. Any comparison logic you want (fuzzy
matching, checking multiple fields, calling another LLM as a judge)
goes in this one method.

## Running it

```bash
uv run python lessons/pydantic_ai/02_intermediate/19_intermediate_checkpoint_project/lesson.py
```

## Checkpoint

Before moving on to the advanced tier, you should be able to explain,
without looking back at earlier lessons:

- Why a tool function calling `other_agent.run_sync(...)` is enough for
  multi-agent delegation, no special "multi-agent" API needed.
- What determines which member of a `Union` output type actually comes
  back on a given run.
- Why usage passed through delegated calls (`usage=ctx.usage`) matters
  for tracking the true cost of a triage system.
- How a custom `Evaluator` subclass differs from a built-in one like
  `EqualsExpected`.

If any of those feel shaky, revisit that lesson before starting the
advanced tier, which builds on all of this without re-explaining it.
