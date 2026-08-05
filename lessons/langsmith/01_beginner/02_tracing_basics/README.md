# Lesson 2: Nested traces, and the run tree they form

## What we're building

Three `@traceable` functions, where one (`analyze`) calls the other two
(`clean`, `count_words`). Lesson 1 traced a single, isolated function
call. Real programs are never that flat, so this lesson shows what
LangSmith does when traced calls happen inside other traced calls.

## What this reveals

LangSmith doesn't need to be told about the relationship between
`analyze`, `clean`, and `count_words`. It detects that `clean` and
`count_words` were called while `analyze`'s run was still active, and
records them as **child runs** of `analyze`. The result, in the UI, is a
**run tree**: `analyze` at the top, `clean` and `count_words` nested
underneath it, each with its own inputs, outputs, and timing.

This matters because real applications are call stacks many levels
deep. Without nesting, you'd see a flat list of runs with no way to tell
which calls belonged to which request. With it, you can open one
top-level run and see everything that happened underneath it, in order.

## The code, piece by piece

```python
@traceable
def clean(text: str) -> str:
    return text.strip().lower()

@traceable
def count_words(text: str) -> int:
    return len(text.split())
```

Two small, independently traceable functions, nothing new here from
Lesson 1.

```python
@traceable
def analyze(text: str) -> dict:
    cleaned = clean(text)
    word_count = count_words(cleaned)
    return {"cleaned": cleaned, "word_count": word_count}
```

`analyze` is also `@traceable`, and it calls the other two functions
during its own execution. That's the entire mechanism: nesting comes
for free from ordinary function calls, there's no special API for
"parent" and "child" runs to configure.

## Running it

```bash
uv run python lessons/langsmith/01_beginner/02_tracing_basics/lesson.py
```

In the UI, find the `analyze` run and click it. Notice `clean` and
`count_words` appear indented underneath it, in the order they actually
ran.

## Checkpoint

- **Nesting is automatic**: a `@traceable` function called from inside
  another `@traceable` function becomes a child run, no configuration
  needed.
- **Run tree**: the parent/child structure of runs shown in the UI,
  matching your actual call stack.
- **Why it matters**: lets you inspect one top-level request and see
  every step that contributed to it, in the order it happened.

If anything here still feels unclear, ask before moving to Lesson 3.
