# Lesson 23: Refactoring into tools() and run_agent()

## Where we left off

Every lesson since Lesson 20 has hand-rolled a list of documents and a
hand-rolled tool registry, rebuilt from scratch inside `main()`. This
lesson draws the same boundary [naive_rag Lesson 23](../../../naive_rag/03_advanced/23_refactoring_into_ingest_and_ask/README.md)
drew for a plain retrieval pipeline, `ingest()` (expensive, once) and
`ask()` (cheap, per question), applied to this course's agent loop, and
graduates the hand-rolled list-based store to a real vector database,
`chromadb`, the same graduation [naive_rag Lesson 20](../../../naive_rag/03_advanced/20_introducing_chromadb/README.md)
made.

## What lives inside `State`

```python
State = tuple[chromadb.Collection, ToolRegistry]
```

This course's `State`, the thing `ingest()` returns and `ask()`
consumes, is a two-tuple: a ready-to-query `chromadb.Collection`
(everything `search_notes()` needs to retrieve), and a `ToolRegistry`
(`dict[str, Tool]`, Lesson 21's registry, already built against that
same collection). Anything downstream holding a `State`, a script's
`main()`, [Lesson 24](../24_wrapping_it_as_a_service/README.md)'s
FastAPI service, or a later course's router, can call
`ask(query, state, k)` without knowing chromadb, function calling, or
this course's specific toolset are involved at all. This is stated
explicitly here, rather than left implicit, specifically so
`adaptive_rag` Lesson 21 (a later course in this series) can wire this
strategy in by reading this paragraph, not this file's full
implementation.

## The code, piece by piece

```python
def tools(collection: chromadb.Collection) -> ToolRegistry:
    return {"search_notes": Tool(..., fn=lambda query: search_notes(query, collection)), ...}
```

Lesson 21's `build_registry()`, renamed `tools()` to match this
course's spec, and repointed at a `chromadb.Collection` instead of a
plain Python list, everything else about it (declaration and function
bundled together, one dict entry per tool) is unchanged.

```python
def run_agent(query: str, registry: ToolRegistry, max_steps: int = MAX_STEPS) -> str:
    ...
```

Lesson 21's loop, unchanged.

```python
def ingest(notes_dir: Path, chroma_client) -> State:
    ...
    registry = tools(collection)
    return collection, registry

def ask(query: str, state: State, k: int = 1) -> str:
    _, registry = state
    return run_agent(query, registry)
```

`ingest()` does the expensive, once-per-run work: embed every note,
load it into a fresh `chromadb` collection, build the tool registry
against that collection, and return both as `State`. `ask()` does the
cheap, per-question work: unpack the registry from `State`, hand it to
`run_agent()`. This is `tools()` + `run_agent()` at the inner boundary,
`ingest()` + `ask()` at the outer one, both boundaries this course's
spec asked for, drawn in the same two functions.

## Why `k` is accepted but only loosely used

The series' `ask(query, state, k)` signature includes `k`, the number
of chunks to retrieve, because every other course's retrieval genuinely
varies with it. This course's `search_notes()` tool always retrieves
one document per call, by design, since Lesson 10: a question needing
facts from multiple documents gets that by calling the tool again, not
by asking for a bigger `k` in one call. `ask()` still accepts `k` for
signature compatibility with the rest of the series, worth stating
explicitly rather than leaving as an unexplained unused parameter.

## Running it

```bash
uv run python lessons/agentic_rag/03_advanced/23_refactoring_into_tools_and_run_agent/lesson.py
```

## Expected output

```
Ingested 5 documents into chromadb, 3 tools registered

Q: How often does the sourdough starter need feeding at room temperature?
A: The sourdough starter needs feeding every 12 hours at room temperature.

Q: What is 15 times 6?
A: 90
```

## Checkpoint

- **`State = tuple[chromadb.Collection, ToolRegistry]`**: this course's
  answer to the series' shared Strategy protocol, a ready collection
  plus a registry already built against it.
- **`ingest(notes_dir, chroma_client) -> State`**: expensive, runs
  once.
- **`ask(query, state, k) -> str`**: cheap, runs per question, wraps
  `run_agent()` internally.
- `tools()` and `run_agent()` are this course's inner boundary; `ingest()`
  and `ask()` are the series' shared outer boundary, wrapping them.

If anything here still feels unclear, ask before moving to Lesson 24.
