# Lesson 5: Dependency injection with `RunContext`

## The problem: passing runtime state without globals

In the `langchain` course, if a tool needed access to something like a
database connection or the current user's ID, you'd usually reach for
a closure, a global, or stuff it awkwardly into the prompt. Pydantic AI
gives this a first-class mechanism: `deps_type` and `RunContext`.

## Declaring what an agent depends on

```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class AppDeps:
    user_name: str
    is_admin: bool

agent = Agent("google:gemini-3.5-flash-lite", deps_type=AppDeps)
```

`deps_type` is just documentation-as-a-type: it tells Pydantic AI (and
your type checker) what shape of object every `run_sync` call must
supply as `deps=`. It can be a dataclass, a plain class, a dict, an
open database connection, whatever your agent's tools and prompts
actually need at runtime.

## Reading deps inside the run

Any function that Pydantic AI calls during a run, a dynamic system
prompt, a tool, an output validator, can accept a `RunContext[Deps]` as
its first parameter and read `ctx.deps` off it:

```python
@agent.system_prompt
def greet(ctx: RunContext[AppDeps]) -> str:
    return f"The user's name is {ctx.deps.user_name}."
```

```python
result = agent.run_sync("Hello!", deps=AppDeps(user_name="Nolan", is_admin=False))
```

Notice deps are passed to `run_sync`, not to `Agent(...)`. The agent
object is stateless and reusable across many runs and many different
callers; the deps are what makes each individual run specific to one
user or one request. This is the same shape as constructing a
LangChain agent once and passing per-request context through
`RunnableConfig`, just typed end to end.

## Running it

```bash
uv run python lessons/pydantic_ai/01_beginner/05_dependency_injection/lesson.py
```

## Checkpoint

- `deps_type=` on `Agent(...)` declares what shape of runtime state the
  agent expects.
- `deps=` on `run_sync(...)` supplies the actual value, per run, not
  per agent.
- `RunContext[Deps]` is how tools, dynamic system prompts, and output
  validators all read `ctx.deps`.

If anything here still feels unclear, ask before moving to Lesson 6,
where tools use exactly this mechanism.
