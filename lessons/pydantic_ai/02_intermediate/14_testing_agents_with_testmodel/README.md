# Lesson 14: Testing agents with `TestModel`

## `defer_model_check`, so this lesson needs no API key

Constructing `Agent("google:gemini-3.5-flash-lite")` normally resolves
the Gemini provider immediately, which fails without `GOOGLE_API_KEY`
set, even if you plan to override the model before ever calling it.
Passing `defer_model_check=True` skips that eager check, so an agent
meant to be tested (or run entirely under `TestModel`) doesn't need
real credentials at all until you actually call the real model.

## The problem: agent logic shouldn't require a live API call to test

Everything you've built so far calls Gemini for real. That's fine for
learning, but a real test suite calling a live LLM on every run is
slow, flaky, and costs money for behavior (a tool's own logic, an
output validator's rules) that has nothing to do with what the model
actually says. `TestModel` swaps in a fake model that never makes a
network call.

## `agent.override(model=...)`

`agent.override` is a context manager that temporarily replaces an
agent's model, everything else about the agent (tools, deps,
output_type, validators) stays exactly as defined:

```python
from pydantic_ai.models.test import TestModel

with agent.override(model=TestModel()):
    result = agent.run_sync("add 2 and 3")
```

By default, `TestModel()` calls every tool the agent has registered
(`call_tools="all"`), with dummy arguments generated from each tool's
schema (a `0` for an `int`, an empty string for a `str`, etc.), then
returns a synthetic output. This is enough to verify things like "does
this tool get called at all," "does my output validator reject a bad
value," or "does the agent have the tools I think it has," all without
depending on what Gemini decides to do on a given day.

## Forcing a specific output

For assertions on your own logic rather than the model's behavior,
`custom_output_args` pins exactly what comes back, still passed
through real validation:

```python
class Answer(BaseModel):
    value: int

with agent.override(model=TestModel(custom_output_args={"value": 42})):
    result = agent.run_sync("whatever")
    assert result.output.value == 42
```

This is the closest Pydantic AI equivalent to mocking a LangChain
model's `.invoke()` return value, except the fake output still runs
through your real `output_type` validation and `output_validator`
functions, so a test using `TestModel` still exercises your actual
validation logic, not just your test's assumptions about it.

## Running it

```bash
uv run python lessons/pydantic_ai/02_intermediate/14_testing_agents_with_testmodel/lesson.py
```

## Checkpoint

- `agent.override(model=TestModel())` swaps out the model only, tools
  and validators stay real.
- Default `TestModel()` auto-calls every registered tool with dummy
  arguments, useful for verifying tools are wired up correctly.
- `custom_output_args=` pins a specific output, still validated for
  real, useful for testing your own validation/business logic in
  isolation from the model.

If anything here still feels unclear, ask before moving to Lesson 15,
where we move from ad-hoc tests to a proper eval dataset.
