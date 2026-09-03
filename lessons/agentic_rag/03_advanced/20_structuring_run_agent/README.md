# Lesson 20: Structuring run_agent()

## Where we left off

Lesson 19 showed one specific way `if/elif` dispatch breaks: the
declared-tools list and the dispatch logic live in different places
with nothing keeping them in sync. Before fixing that (Lesson 21), this
lesson fixes a related but separate problem: every earlier lesson's
loop mechanics (build a transcript, call the model, run a tool, repeat)
were tangled together with the specific tools being dispatched, inside
one function. This lesson pulls them apart.

## The code, piece by piece

```python
DispatchFn = Callable[[types.FunctionCall], dict[str, str]]

def run_agent(query: str, dispatch: DispatchFn, max_steps: int = MAX_STEPS) -> str:
    ...
    result = dispatch(call)
    ...
```

`run_agent()` is every loop this course has built since Lesson 14,
with one deliberate change: instead of an `if call.name == "search_notes": ...`
chain living inside the loop, it calls `dispatch(call)`, a plain
function passed in as an argument. `run_agent()` has no idea
`search_notes` or `get_current_datetime` exist. It knows how to run a
loop; it does not know what the loop is for.

```python
def make_dispatch(store: list[dict]) -> DispatchFn:
    def dispatch(call: types.FunctionCall) -> dict[str, str]:
        ...
    return dispatch
```

Everything tool-specific moved here: the `if/elif` chain, the
`store` it needs, the try/except error handling from Lesson 16. This
function knows exactly what `run_agent()` doesn't, which tools exist
and how to run them, and nothing about how the surrounding loop works.

## Why separating these two things matters

This is a **separation of concerns**: "how does an agent loop work" is
a different question from "which tools does this particular agent
have," and Lessons 5 through 19 answered both questions inside the same
function, every time. Once they're separate, `run_agent()` becomes
reusable in a way it wasn't before, a completely different assistant,
with a completely different toolset, could reuse this exact
`run_agent()` unmodified, just by supplying a different `dispatch`
function. Lesson 19's bug (a tool declared but not dispatched) becomes
strictly a `make_dispatch()` problem now too, not a bug that could also
hide inside loop logic, since loop logic no longer touches tool names
at all.

## Running it

```bash
uv run python lessons/agentic_rag/03_advanced/20_structuring_run_agent/lesson.py
```

## Expected output

```
Q: How often should the vinyl records get a dust brush before playing?
A: Records get an anti-static brush pass before every play, no exceptions.

Q: What time is it right now in Lisbon?
A: <the current date and time in Europe/Lisbon>
```

## Checkpoint

- **`run_agent(query, dispatch, max_steps)`**: pure loop mechanics, no
  knowledge of what tools exist.
- **`make_dispatch(store)`**: pure tool knowledge, no knowledge of how
  the surrounding loop works.
- Separating these makes `run_agent()` reusable across different
  toolsets without modification, the same benefit
  [naive_rag Lesson 23](../../../naive_rag/03_advanced/23_refactoring_into_ingest_and_ask/README.md)
  got from separating `ingest()` from `ask()`.
- This still uses an `if/elif` inside `make_dispatch()`, Lesson 19's
  actual bug (declared-but-undispatched tools) isn't fixed yet, only
  relocated somewhere it's easier to fix next.

If anything here still feels unclear, ask before moving to Lesson 21.
