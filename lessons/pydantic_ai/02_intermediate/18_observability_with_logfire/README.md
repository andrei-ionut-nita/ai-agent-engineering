# Lesson 18: Observability with Logfire

## The `langsmith` tracing equivalent

The `langsmith` course wired up tracing by setting environment
variables and letting every LangChain call get picked up automatically.
Pydantic AI's observability story is built on the same underlying
standard, OpenTelemetry, via Pydantic's own `logfire` package, which
you can point at Logfire's hosted UI, or, as this lesson does, keep
entirely local by printing spans straight to your console.

## Instrumenting an agent

Two calls turn tracing on: configure `logfire` itself, then tell it to
instrument Pydantic AI specifically.

```python
import logfire

logfire.configure(send_to_logfire=False)  # local only, no account needed
logfire.instrument_pydantic_ai()

agent = Agent("google:gemini-3.5-flash-lite")
result = agent.run_sync("Say hi in one word.")
```

With that in place, every agent run emits a span (`agent run`) with
nested child spans for each model call (`chat gemini-3.5-flash-lite`)
and each tool invocation, printed to the console as they happen. This
is the same "see the whole run's tree of calls" value LangSmith's trace
view provides, just rendered locally instead of on a hosted dashboard.

## Going further: a real Logfire project

Flipping `send_to_logfire=False` to `True` (and setting a
`LOGFIRE_TOKEN`) sends the exact same spans to Logfire's hosted UI
instead of your console, searchable, filterable, with cost and latency
breakdowns per run. Nothing about the instrumentation call changes,
only the destination. That's the same shape as `langsmith`'s
`LANGSMITH_TRACING=true` switch: local development doesn't require the
hosted service, but the same code scales up to it without modification.

## Running it

```bash
uv run python lessons/pydantic_ai/02_intermediate/18_observability_with_logfire/lesson.py
```

## Checkpoint

- `logfire.configure(send_to_logfire=False)` plus
  `logfire.instrument_pydantic_ai()` traces every agent run to your
  console, no account needed.
- Spans nest: one `agent run` span per `run_sync` call, with child
  spans for model calls and tool invocations.
- This is the `langsmith` tracing equivalent, built on OpenTelemetry
  instead of a LangChain-specific integration.

If anything here still feels unclear, ask before moving to Lesson 19,
this tier's checkpoint project.
