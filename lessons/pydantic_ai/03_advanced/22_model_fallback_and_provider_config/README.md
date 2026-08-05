# Lesson 22: Model fallback and provider config

## The problem: one provider having a bad day

Every lesson so far has used one model string. In production, a
single provider having an outage, a bad deployment, a rate limit spike,
shouldn't take your whole agent down. `FallbackModel` wraps a list of
models in priority order and automatically tries the next one if the
current one raises an API error.

```python
from pydantic_ai.models.fallback import FallbackModel

fallback_model = FallbackModel(
    "google:gemini-9.9-does-not-exist",  # deliberately broken, for this demo
    "google:gemini-3.5-flash-lite",       # falls back to this
)

agent = Agent(fallback_model)
result = agent.run_sync("Say hi in one word.")
```

If the first model raises `ModelAPIError` (the default trigger,
covering things like rate limits, timeouts, and 5xx responses),
`FallbackModel` transparently retries the same request against the
next model in the list, no code at the call site changes. You can
narrow or widen which exceptions trigger a fallback with `fallback_on=`
if you want a stricter or looser policy than "any API error."

## Swapping models without touching agent code

Because `Agent(model)` accepts any model string or `Model` instance,
the actual model an agent uses is entirely a construction-time detail.
Swapping Gemini for a different provider, or wrapping it in a
`FallbackModel`, or overriding it for tests (Lesson 14), never requires
changing a tool, a system prompt, or an output type. The agent's
*behavior* (what it does, what it returns) and its *model* (which LLM
answers) are cleanly separated.

## Where this fits with `agent.override`

Lesson 14 used `agent.override(model=TestModel())` to swap models for
testing. `FallbackModel` is the same idea applied to production
reliability instead of testing: both are ways of changing "which model
answers this request" without touching the rest of the agent's
definition.

## Running it

```bash
uv run python lessons/pydantic_ai/03_advanced/22_model_fallback_and_provider_config/lesson.py
```

## Checkpoint

- `FallbackModel(model_1, model_2, ...)` tries models in order,
  falling back automatically on `ModelAPIError` (configurable via
  `fallback_on=`).
- The rest of the agent, tools, prompts, output types, is unaffected by
  which model (or fallback chain) actually answers.
- This is the production-reliability counterpart to `agent.override`,
  both change the model, not the agent's logic.

If anything here still feels unclear, ask before moving to Lesson 23.
