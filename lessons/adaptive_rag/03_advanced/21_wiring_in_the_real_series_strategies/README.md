# Lesson 21: Wiring in the Real Series Strategies

## Where we left off

Every strategy this course has routed to so far (Lessons 4-6, rebuilt
locally in Lessons 19-20) was a small, hand-rolled stand-in: enough to
demonstrate routing itself, not the real naive, graph, or corrective
retrieval this series already built, hands-on, in their own courses.
This lesson replaces every stand-in with the real thing: the actual
`ingest()`/`ask()` functions from `naive_rag`, `hybrid_rag`, `graph_rag`,
`corrective_rag`, and `agentic_rag`'s own Lesson 23, imported and called
directly, not reimplemented.

## Why this lesson is straightforward, not five separate integrations

This only works cleanly because all five courses already converged on
the same shape, deliberately, as `docs/RAG-SERIES-PLAN/README.md`'s
"Shared Strategy Protocol" section describes: `ingest(...) -> State`,
`ask(query, state, k) -> str`. This lesson composes five conforming
implementations, it does not reconcile five bespoke ones.

```python
def _load_lesson_module(name: str, relative_path: str) -> ModuleType:
    file_path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, file_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
```

Every course's Lesson 23 lives in a folder starting with a digit
(`23_refactoring_into_ingest_and_ask`), which a normal `import` statement
can't name (Python identifiers can't start with a digit). This is the
standard workaround: load a module straight from its file path with
`importlib.util`, no package or importable name required.

```python
naive = _load_lesson_module("naive_lesson23", "lessons/naive_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py")
hybrid = _load_lesson_module("hybrid_lesson23", "lessons/hybrid_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py")
graph = _load_lesson_module("graph_lesson23", "lessons/graph_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py")
corrective = _load_lesson_module("corrective_lesson23", "lessons/corrective_rag/03_advanced/23_refactoring_into_ingest_grade_correct_ask/lesson.py")
agentic = _load_lesson_module("agentic_lesson23", "lessons/agentic_rag/03_advanced/23_refactoring_into_tools_and_run_agent/lesson.py")
```

Five real, already-verified implementations, loaded once, at the top of
this lesson.

## The one real wrinkle: argument shape, not protocol drift

`ingest()`'s exact input differs slightly across courses: `naive_rag` and
`agentic_rag` both take `(notes_dir, chroma_client)` because they build
their collection against a caller-supplied client; `hybrid_rag` and
`corrective_rag` take `notes_dir` alone and build their own client
internally; `graph_rag` takes `docs: list[Path]` instead of a directory,
since it processes documents one at a time to extract relationships.
Every `ask()`, across all five, still takes `(query, state, k)` and
returns a string, unchanged. This lesson adapts to each `ingest()`'s
existing shape, once, per course:

```python
def ingest_graph() -> object:
    return graph.ingest(sorted(NOTES_DIR.glob("*.md")))
```

That's calling `graph_rag`'s real `ingest()` with the argument shape
`graph_rag`'s own Lesson 23 already defined, not reimplementing anything
about how graph traversal works. This is what "composing five conforming
implementations" means: five real functions, called correctly, not five
retrieval mechanics rewritten inside this course's router.

## One deliberate, scoped fix: chromadb collection isolation

Four of the five courses' Lesson 23 all name their in-memory chromadb
collection `"notes"`, and chromadb's default client is a shared,
process-wide store. Ingesting all five back to back in one process, as
this lesson's demo does, would otherwise have each later `ingest()` step
on the collection an earlier one just built. This lesson gives
`naive_rag` and `agentic_rag` their own isolated `PersistentClient`
(they accept a client argument, so this is just passing a different one
in), and briefly patches `chromadb.Client` for `hybrid_rag` and
`corrective_rag` (which build their own client internally, with no way
to inject one from outside) so each strategy's storage is fully
isolated. This is scoped entirely to this lesson's file, none of the
five courses' own files changed.

## Running it

```bash
uv run python lessons/adaptive_rag/03_advanced/21_wiring_in_the_real_series_strategies/lesson.py
```

## Expected output

```
Ingesting this course's fixtures through all five real Advanced-tier strategies...

  naive: ingested
  hybrid: ingested
  graph: ingested
  corrective: ingested
  agentic: ingested

Same question, asked through all five real implementations:
Q: What two hobbies happen in the same room as the weather station?

[naive] <naive's real top-2 answer, sometimes correct, sometimes not, exactly the honest limit naive_rag's own Lesson 16 already demonstrated>
[hybrid] <hybrid's real fused answer, typically correctly naming bookshelf organization and cello practice>
[graph] <graph's real traversal answer>
[corrective] <corrective's real graded answer>
[agentic] <agentic's real tool-calling answer>
```

Every answer above comes from the real course, unmodified. Any
difference in quality between them here is the same honest difference
each course's own Lesson 26 already named, not something this lesson
introduces.

## Checkpoint

- `ingest(...) -> State` / `ask(query, state, k) -> str`, the series'
  shared Strategy protocol, is what makes wiring five real courses in
  behind one router straightforward instead of a five-way reconciliation
  project.
- `importlib.util.spec_from_file_location` loads a module by file path,
  the standard workaround for a folder name that starts with a digit and
  can't be named in a normal `import` statement.
- A signature drift can be genuine (the protocol violated) or cosmetic
  (the same contract, expressed with a slightly different argument
  shape each course's own Lesson 23 already committed to). This lesson's
  five courses are the cosmetic case: every `ask()` matches exactly, and
  every `ingest()` still returns a `State` an `ask()` can consume, only
  the input argument's shape varies. Reconciling that here, at the call
  site, rather than inside any of the five courses' own files, is what
  keeps each course's already-verified Lesson 23 untouched.

If anything here still feels unclear, ask before moving to Lesson 22.
