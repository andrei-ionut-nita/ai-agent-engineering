# Lesson 13: Usage limits and cost tracking

## Every result carries its own usage stats

`result.usage` (a property, not a method) is a `RunUsage` with request
count, input tokens, and output tokens for that run:

```python
result = agent.run_sync("Say hi.")
print(result.usage)
# RunUsage(requests=1, input_tokens=4, output_tokens=2, ...)
```

This is the same information `LangSmith` traces show you per run in
the `langsmith` course, just available locally on every result, no
tracing backend required to see it.

## Capping usage before it happens

`UsageLimits` lets you cap a run *before* it runs away: a maximum
number of model requests (useful for agentic loops that could keep
calling tools forever), or a maximum token count (useful for cost
control).

```python
from pydantic_ai import UsageLimits

result = agent.run_sync(
    "Say hi.",
    usage_limits=UsageLimits(total_tokens_limit=500),
)
```

If a run would exceed the limit, Pydantic AI raises
`UsageLimitExceeded` instead of quietly letting the bill grow. This is
a real safety mechanism, not just an observability nicety: an agent
stuck in a tool-calling loop against a limit you didn't set could
otherwise burn through your Gemini quota with no natural stopping
point.

## Limits compose with delegation

Because Lesson 12's delegated calls pass `usage=ctx.usage` through, a
`usage_limits=` set on the *outer* run's `run_sync` call caps the
combined total across every delegated agent call too, not just the
top-level agent. One limit protects the whole call tree.

## Running it

```bash
uv run python lessons/pydantic_ai/02_intermediate/13_usage_limits_and_cost_tracking/lesson.py
```

## Checkpoint

- `result.usage` (a property) reports requests/tokens for that run,
  available on every `AgentRunResult` with no tracing setup needed.
- `UsageLimits(...)` passed as `usage_limits=` raises
  `UsageLimitExceeded` before a run blows past your budget.
- Limits set on an outer run apply to the whole call tree, including
  delegated sub-agent calls that pass `usage=` through.

If anything here still feels unclear, ask before moving to Lesson 14,
where we test agents without spending any tokens at all.
