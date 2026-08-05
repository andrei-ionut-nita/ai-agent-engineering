# Lesson 9: Streaming output with `run_stream`

## Why stream

`run_sync` waits for the entire answer before returning anything, fine
for short answers, frustrating for a long one where a user is staring
at a blank screen. `run_stream` gives you the output incrementally, as
the model produces it, the same motivation as `.stream()` on a
LangChain runnable.

```python
async with agent.run_stream("Count from 1 to 5.") as result:
    async for chunk in result.stream_output():
        print(chunk)
```

`run_stream` is an async context manager (there's no `_sync` version,
streaming is inherently async), so it needs an `async def main()` and
`asyncio.run(main())`, same as the async lessons in the `mcp` course.

## Streaming structured output, not just text

The genuinely different part, compared to LangChain streaming, is that
this works for structured `output_type`s too, not just plain text:

```python
class Fact(BaseModel):
    city: str
    country: str

agent = Agent("google:gemini-3.5-flash-lite", output_type=Fact)

async with agent.run_stream("Tell me about Tokyo.") as result:
    async for partial in result.stream_output():
        print(partial)  # Fact(city='Tokyo', country='Japan'), rebuilt each chunk
```

Each item yielded by `stream_output()` is a fully re-validated instance
of your output type, built from however much of the response has
arrived so far (fields may be missing or partial early on, then
complete by the last chunk). This lets a UI render a structured card
that fills itself in, instead of a wall of streaming JSON text you'd
have to parse yourself.

## Running it

```bash
uv run python lessons/pydantic_ai/01_beginner/09_streaming_output/lesson.py
```

## Checkpoint

- `run_stream` is an async context manager; use it inside `async def`
  with `asyncio.run(...)`.
- `async for chunk in result.stream_output()` yields output as it
  arrives, cumulatively.
- With a structured `output_type`, streamed chunks are validated
  instances of that type, not raw text you parse yourself.

If anything here still feels unclear, ask before moving to Lesson 10,
this course's first checkpoint project.
