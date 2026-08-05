# Lesson 1: Turn on tracing and record your first run

## What we're building

A single function decorated with `@traceable`, so that calling it once
sends a record of the call to LangSmith. This is the smallest possible
trace, one function, one input, one output, and it's the foundation
every later lesson builds on.

## Why a separate service

`langchain` and `langgraph` (the last two courses) are libraries: code
that runs on your machine. LangSmith is a hosted service: a place
outside your machine that stores what your code did, so you can look at
it after the fact from a browser. You already have a `GOOGLE_API_KEY` in
`.env` for talking to Gemini; now you need a second, unrelated key,
`LANGSMITH_API_KEY`, for talking to LangSmith. Get one free at
[smith.langchain.com](https://smith.langchain.com), then add to `.env`:

```
LANGSMITH_API_KEY=your-key-here
LANGSMITH_TRACING=true
```

`LANGSMITH_TRACING=true` is the master switch. Without it, `@traceable`
functions run exactly as normal Python, nothing is sent anywhere.

## The code, piece by piece

```python
from langsmith import traceable
```

`traceable` is a **decorator**, a function that wraps another function
to add behavior around it without changing its body.

```python
@traceable
def summarize(text: str) -> str:
    ...
```

Putting `@traceable` directly above a function means: every time
`summarize(...)` is called, first record the arguments it was given,
then run the real function body, then record what it returned (or, if
it raised an exception, record that instead). All of this happens in
the background over the network; the function's own behavior is
unchanged.

```python
result = summarize("LangSmith records ...")
```

An ordinary function call. Nothing about calling `summarize` looks any
different from calling any other function, tracing is invisible from
the caller's side.

## Running it

```bash
uv run python lessons/langsmith/01_beginner/01_setup_and_first_trace/lesson.py
```

Then open [smith.langchain.com](https://smith.langchain.com), go to your
default project, and find the run named `summarize`. Click it: you'll
see the exact input string and the exact output string, plus a latency
number, all recorded automatically.

## Expected output

No AI model is involved, so the terminal output is exact:

```
20 words, starts with: LangSmith records what happens every...
```

If nothing shows up in the LangSmith UI, double-check `.env` has both
`LANGSMITH_API_KEY` and `LANGSMITH_TRACING=true`, then see the
[Troubleshooting section](../../../../README.md#troubleshooting) in
this project's root README.

## Checkpoint

- **LangSmith**: a hosted service that records what your traced code
  did, separate from LangChain/LangGraph, which run locally.
- **`LANGSMITH_TRACING=true`**: the switch that turns tracing on or off
  globally.
- **`@traceable`**: a decorator that records a function's inputs,
  output, and duration as a "run" every time it's called.
- **Run**: one recorded execution of a traced function, visible in the
  LangSmith UI.

If anything here still feels unclear, ask before moving to Lesson 2.
