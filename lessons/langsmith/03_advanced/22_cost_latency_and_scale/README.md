# Lesson 22: Token usage, latency, and cost, at the scale of many runs

## What we're building

One direct look at a single call's token usage, then the same numbers
pulled across every recent `"llm"` run in the project and summed,
averaged, and maxed, the difference between "how much did this one
request cost" and "how much is this application costing and how fast is
it, overall."

## What this reveals

Every LLM call has a real cost (measured in tokens, and from tokens, in
money) and a real duration. For one call, that's easy to eyeball: Gemini
returns `usage_metadata` directly on the response. The moment you have
more than a handful of calls, though, eyeballing stops working, you need
the same numbers, aggregated, across runs you didn't watch happen live.
That's exactly what recording every run's tokens, cost, and latency
inside LangSmith buys you: `list_runs` (Lesson 18) returns those fields
on every run, ready to sum and average, without needing to have
inspected any individual call yourself.

This is the concrete link between "we're tracing everything" (the whole
Beginner tier) and "is this application efficient." A trace isn't just
for debugging correctness, the exact same recorded data answers
capacity-planning and cost questions too, for free, because it was
already being captured.

## The code, piece by piece

```python
response = model.invoke("...")
usage = response.usage_metadata
```

`usage_metadata` is a dict LangChain attaches to every chat model
response: `input_tokens`, `output_tokens`, `total_tokens`. This is local
information, available even with tracing off, LangSmith just also
records it on the corresponding `"llm"` run.

```python
llm_runs = list(client.list_runs(project_name=PROJECT_NAME, run_type="llm", limit=50))
total_tokens = sum(run.total_tokens or 0 for run in llm_runs)
total_cost = sum(run.total_cost or 0 for run in llm_runs)
```

Every `"llm"` run carries the same token counts (and, where LangSmith
has pricing data for the model, an estimated `total_cost`) as fields on
the run object itself, `or 0` guards against a run where these fields
weren't populated (for instance, a free-tier model LangSmith has no
listed price for).

```python
latencies = [(run.end_time - run.start_time).total_seconds() for run in llm_runs if run.end_time is not None]
```

The same latency calculation as Lesson 18, applied specifically to
`"llm"` runs, since model calls are usually the slowest part of any
chain.

## Running it

```bash
uv run python lessons/langsmith/03_advanced/22_cost_latency_and_scale/lesson.py
```

Run several earlier lessons first for a more meaningful aggregate. You
should see one call's token counts printed directly, followed by
totals, an average latency, and a slowest-run time across all recent
`"llm"` runs.

## Checkpoint

- **`response.usage_metadata`**: per-call token counts, available
  locally on any chat model response.
- **`run.total_tokens` / `run.total_cost`**: the same figures, recorded
  on every traced `"llm"` run, queryable in aggregate via `list_runs`.
- **Why this matters at scale**: tracing already captures what you need
  to answer cost and performance questions across an entire
  application, not just correctness questions about individual calls.

If anything here still feels unclear, ask before moving to Lesson 23.
