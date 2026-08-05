# Lesson 10 (Checkpoint): A validated research-notes assistant

## What you're building

An agent that researches a topic (using a fake "search" tool, so this
runs with no external API), then returns a validated `ResearchNote`,
and saves it into an in-memory notes store via a second tool. This
exercises every beginner-tier concept in one place:

- **`output_type`** (Lesson 3): the final answer is a `ResearchNote`
  model, not a string.
- **`deps_type` / `RunContext`** (Lesson 5, 7): the notes store is
  injected as a dependency, not a global.
- **`@agent.tool`** (Lesson 6, 7): `fake_search` and `save_note` are
  both tools, one plain-ish, one reading `ctx.deps`.
- **`@agent.output_validator`** (Lesson 8): rejects a note with no key
  points or an out-of-range confidence score.

## The shape of `ResearchNote`

```python
class ResearchNote(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    confidence: float  # 0.0 to 1.0
```

The agent is instructed to call `fake_search` first to gather
"evidence," then `save_note` to persist its findings, then produce the
final `ResearchNote`. You don't write that sequencing logic, the model
decides the order based on the system prompt and the tool
descriptions, same as any multi-tool LangChain agent.

## Running it

```bash
uv run python lessons/pydantic_ai/01_beginner/10_beginner_checkpoint_project/lesson.py
```

## Checkpoint

Before moving on to the intermediate tier, you should be able to
explain, without looking back at earlier lessons:

- Why `deps=` goes on `run_sync`, not on `Agent(...)`.
- What happens, mechanically, when the model calls a tool mid-run.
- Why raising `ModelRetry` in an output validator is different from
  just returning `None` on failure.
- What changes about `result.output`'s type when you set
  `output_type=SomeModel` versus leaving it as the default.

If any of those feel shaky, revisit that lesson before starting the
intermediate tier, which builds on all of this without re-explaining
it.
