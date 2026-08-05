# Lesson 2: Your first agent

## `Agent`, the one class you'll use constantly

Everything in Pydantic AI starts with an `Agent`. At minimum it needs a
model string:

```python
from pydantic_ai import Agent

agent = Agent("google:gemini-3.5-flash-lite")
```

The model string is `"<provider>:<model-name>"`. `google` is the
Gemini provider, reading `GOOGLE_API_KEY` from the environment exactly
like `ChatGoogleGenerativeAI` did in the `langchain` course, just
without you having to import a separate provider class for the common
case.

## Running an agent

`run_sync` is the simplest way to call an agent: give it a prompt, get
a result back.

```python
result = agent.run_sync("What is the capital of France?")
print(result.output)
```

`result` isn't just the answer, it's an `AgentRunResult` object holding
the output, the full message history, and usage stats. You'll use
those other fields starting in Lesson 11. For now, `result.output` is
all you need: with no `output_type` specified, it defaults to `str`,
so this behaves exactly like `model.invoke(...).content` did in
`langchain`.

There's also an async `run` and a streaming `run_stream` (Lesson 9).
`run_sync` is a thin wrapper that runs the async version for you, use
it anywhere you're not already inside an `async def`.

## Running it

```bash
uv run python lessons/pydantic_ai/01_beginner/02_first_agent/lesson.py
```

## Checkpoint

- `Agent("google:gemini-3.5-flash-lite")` creates an agent against
  Gemini, no client object to construct separately.
- `agent.run_sync(prompt)` returns an `AgentRunResult`; `.output` is
  the actual answer.
- With no `output_type`, the output is a plain `str`, same shape as a
  LangChain `model.invoke(...).content` call.

If anything here still feels unclear, ask before moving to Lesson 3,
where the output stops being a plain string.
