# Lesson 17: lfx, the standalone executor

## Where we left off

Every earlier lesson imported Langflow components from inside a Python
script (`from lfx.components... import ...`). `lfx` is also its own
command-line tool, installed alongside `langflow` in this repo but
usable entirely on its own: point it at a `flow.json` and an input, get
an answer back, no Python script required at all.

## Why this matters

A CI pipeline that just needs to smoke-test a flow, or a cron job that
runs one on a schedule, doesn't need the full `langflow` package, a
running server, or even a `.py` file. `lfx run` is the smallest
possible way to execute a flow: one shell command, one process, exits
when it's done.

## Do this yourself

```bash
uv run lfx run lessons/langflow/01_beginner/02_first_flow/flow.json \
  "Say hello in exactly three words." -f text
```

Run this directly in your terminal, no `lesson.py` involved. `-f text`
prints just the answer, drop it (or try `-f json`) to see the full
structured result Langflow builds internally, the same shape
`run_flow_from_json` returns as a Python object.

## The code, piece by piece

```python
subprocess.run(
    [sys.executable, "-m", "lfx", "run", str(FLOW_PATH), input_value, "-f", "text"],
    capture_output=True,
    text=True,
    check=True,
)
```

`lesson.py` shells out to the exact same command from "Do this
yourself", via `subprocess`, so this repo's usual `uv run python
lesson.py` convention keeps working. In a real CI pipeline you'd run
the `lfx run ...` line directly, this wrapper exists only so this
course's own pattern (one runnable `lesson.py` per lesson) holds here
too.

## Running it

```bash
uv run python lessons/langflow/03_advanced/17_lfx_headless_execution/lesson.py
```

## Expected output

Approximate, Gemini's exact phrasing varies:

```
lfx CLI said: Hello to you.
```

## Checkpoint

- **`lfx run <flow.json> <input> -f text`**: the smallest way to
  execute a flow, one shell command, no Python script, no server.
- **when this matters**: CI smoke tests, scheduled jobs, anywhere a
  flow needs to run without the overhead of `langflow run`'s full
  server.

If anything here still feels unclear, ask before moving to Lesson 18.
