# Lesson 7: Tools that read `RunContext.deps`

## `@agent.tool`: tools with access to runtime state

Lesson 6's `add` tool needed nothing but its own arguments. Most real
tools need something more: a database connection, an API client, the
current user's permissions. `@agent.tool` (no `_plain`) gives the tool
function a `RunContext[Deps]` as its first parameter, the same
mechanism Lesson 5 used for dynamic system prompts.

```python
@dataclass
class AppDeps:
    notes: dict[str, str]

agent = Agent("google:gemini-3.5-flash-lite", deps_type=AppDeps)

@agent.tool
def save_note(ctx: RunContext[AppDeps], title: str, body: str) -> str:
    """Save a note under a title."""
    ctx.deps.notes[title] = body
    return f"Saved note '{title}'."
```

The model never sees `ctx`, it only sees the schema for `title` and
`body`. Pydantic AI injects the `RunContext` for you when it calls the
function. This is the exact analog of a LangChain tool that closes
over a shared object, except here the dependency is explicit,
type-checked, and swappable per run instead of baked into the tool at
definition time.

## Why this beats a closure

Because `deps` are supplied fresh on every `run_sync` call, the same
agent and the same tool definitions can serve completely different
runtime state, a different user's notes dict, a different database
connection, per request, without redefining any tools. That's the
practical payoff of dependency injection: one agent definition, many
isolated runs.

## Running it

```bash
uv run python lessons/pydantic_ai/01_beginner/07_tool_with_deps/lesson.py
```

## Checkpoint

- `@agent.tool` (not `tool_plain`) gives the function a
  `RunContext[Deps]` first parameter.
- `ctx.deps` inside a tool is the same `deps=` value passed to
  `run_sync`, never exposed to the model itself.
- One agent definition can serve many isolated runs, each with its own
  deps, no redefinition needed.

If anything here still feels unclear, ask before moving to Lesson 8,
where we validate what a tool (or the model) hands back.
