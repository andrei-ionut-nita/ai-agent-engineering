# Lesson 4: System prompts, static and dynamic

## Static system prompts

Just like `langchain`'s `SystemMessage`, you can give an agent a fixed
instruction that applies to every run:

```python
agent = Agent(
    "google:gemini-3.5-flash-lite",
    system_prompt="You are a terse pirate. Answer in one short sentence.",
)
```

`system_prompt` also accepts a sequence of strings, which are joined,
useful for composing a prompt out of separate concerns (persona, output
format, constraints) without building one long string by hand.

## Dynamic system prompts

The more interesting case is a system prompt that depends on runtime
information, the current date, the logged-in user's name, that you
don't want baked into the agent at construction time. Decorate a
function with `@agent.system_prompt` instead:

```python
from pydantic_ai import RunContext

@agent.system_prompt
def add_persona(ctx: RunContext[str]) -> str:
    return f"You are speaking to {ctx.deps}. Address them by name."
```

This function runs once at the start of every `run_sync` call, and its
return value is appended to the system prompt for that run. `ctx.deps`
is the same dependency-injection mechanism you'll use for tools in
Lesson 5, here it lets the system prompt itself see runtime state.

You can register as many `@agent.system_prompt` functions as you want;
each one contributes its own piece, static and dynamic prompts combine
rather than one replacing the other.

## Running it

```bash
uv run python lessons/pydantic_ai/01_beginner/04_system_prompts/lesson.py
```

## Checkpoint

- `system_prompt="..."` at construction time: fixed instructions for
  every run, the direct equivalent of a LangChain `SystemMessage`.
- `@agent.system_prompt` decorating a function: a prompt fragment
  computed fresh for each run, with access to `ctx.deps`.
- Multiple system prompt sources combine; they don't overwrite each
  other.

If anything here still feels unclear, ask before moving to Lesson 5,
where dependency injection gets its own lesson.
