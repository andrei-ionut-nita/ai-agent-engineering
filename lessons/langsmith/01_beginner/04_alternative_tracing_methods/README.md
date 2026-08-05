# Lesson 4: Tracing without the @traceable decorator

## What we're building

The same idea as Lesson 1's `@traceable`, two more times, using two
different tools: the `trace()` context manager, and the lower-level
`RunTree` object directly. Same result (a run recorded in LangSmith),
three different ways to get there.

## What this reveals

`@traceable` only works when you can put a decorator directly above a
function's definition. Sometimes you can't: the function comes from a
library you don't control, or you only want to trace part of a
function's body, not the whole thing. `trace()` solves that: it's a
context manager (a `with` block) that traces whatever code runs inside
it, regardless of whether that code is a function you own.

Underneath both `@traceable` and `trace()` is `RunTree`, the actual
object that represents a run: a name, a type, inputs, and (once
finished) outputs. `RunTree` is what you'd reach for if you needed full
manual control, for example, starting a run in one function and ending
it in a completely different one. You won't need this often, but
knowing it's there explains what the decorator and context manager are
doing on your behalf.

(The SDK also ships wrappers like `wrap_openai` for popular clients,
patching a client object so every call it makes is traced automatically,
without `@traceable` or `trace()` at each call site. Not shown here since
this course uses `ChatGoogleGenerativeAI`, which LangChain already
instruments, as seen in Lesson 3.)

## The code, piece by piece

```python
with trace(name="legacy_multiply", run_type="tool", inputs={"a": 6, "b": 7}) as run:
    result = legacy_multiply(6, 7)
    run.end(outputs={"result": result})
```

`trace()` starts the run when the `with` block opens. `run.end(...)`
records the outputs and marks it finished; if you never call `.end()`,
the run stays open in LangSmith with no recorded output, so always call
it (or let an exception propagate, which `trace()` will catch and
record as an error automatically).

```python
run = RunTree(name="manual_run_tree", run_type="chain", inputs={"message": "built by hand"})
run.post()
...
run.end(outputs={"output": output})
run.patch()
```

`RunTree(...)` builds the run object in memory, nothing is sent yet.
`.post()` sends the initial record (name, inputs, start time) to
LangSmith. `.end(...)` records the outputs locally on the object.
`.patch()` sends that update. Two network calls, one at the start, one
at the end, exactly what `@traceable` and `trace()` do for you
automatically.

## Running it

```bash
uv run python lessons/langsmith/01_beginner/04_alternative_tracing_methods/lesson.py
```

In the UI, find `legacy_multiply` and `manual_run_tree` as two separate
top-level runs, each with the inputs/outputs shown above.

## Checkpoint

- **`trace()`**: a context manager that traces a block of code, for
  cases `@traceable` can't reach (code you don't own, or partial
  functions).
- **`RunTree`**: the underlying object every tracing method builds;
  `.post()` sends the start, `.end()` + `.patch()` send the finish.
- **Client wrappers** (`wrap_openai` and similar): patch a client so its
  calls are traced without decorating each call site, not needed here
  since LangChain already instruments `ChatGoogleGenerativeAI`.

If anything here still feels unclear, ask before moving to Lesson 5.
