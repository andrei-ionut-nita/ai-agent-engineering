# Lesson 3: Run types, metadata, and tags

## What we're building

A small pipeline of four traced steps, a fake document search, a word
counter, a Gemini call, and a chain that wires them together, each
labeled with a `run_type` and carrying metadata and tags. This gives
every run in the tree from Lesson 2 an actual category, instead of
everything looking the same.

## What this reveals

`@traceable` accepts a `run_type` argument: `"llm"`, `"chain"`, `"tool"`,
`"retriever"`, and a few others. This isn't just labeling, the LangSmith
UI renders each type differently: an `"llm"` run shows a prompt and
completion side by side, a `"retriever"` run shows the documents it
returned, a `"tool"` run shows the function call and result.

You never had to set `run_type="llm"` for the `model.invoke(...)` call
in `answer_question`. LangChain's `ChatGoogleGenerativeAI` is already
instrumented, so when `LANGSMITH_TRACING=true`, every model call it
makes is automatically recorded as an `"llm"` run and nested under
whatever `@traceable` function called it. Manual `@traceable` and
LangChain's built-in tracing compose together in the same run tree
without any extra work.

`metadata` and `tags` are separate from `run_type`: they're your own
labels. Metadata is a dictionary of arbitrary key/value pairs (here,
which lesson and topic this run belongs to). Tags are a flat list of
short strings, meant for quick filtering (`"beginner"`,
`"langsmith-course"`). Lesson 18 uses both to filter and build
dashboards.

## The code, piece by piece

```python
@traceable(run_type="retriever")
def fake_search(query: str) -> list[str]:
```

Marks this run as a retriever, so the UI shows its return value (a list
of document strings) the way it shows real vector-store results.

```python
@traceable(run_type="tool")
def word_count(text: str) -> int:
```

Marks this as a tool call, distinct from a chain or an LLM call.

```python
@traceable(
    run_type="chain",
    metadata={"lesson": 3, "topic": "run types"},
    tags=["beginner", "langsmith-course"],
)
def answer_question(question: str) -> dict:
```

The top-level run. `run_type="chain"` is actually the default, it's
written explicitly here just to show the parameter exists. `metadata`
and `tags` are attached only to this run, not automatically inherited by
its children (each child run can set its own).

## Running it

```bash
uv run python lessons/langsmith/01_beginner/03_types_of_runs/lesson.py
```

In the UI, open the `answer_question` run tree and notice the icons or
labels next to `fake_search` (retriever), `word_count` (tool), and the
Gemini call (llm) differ from each other and from `answer_question`
(chain). Check the `answer_question` run's metadata/tags panel for the
values set above.

## Checkpoint

- **`run_type`**: categorizes a run (`llm`, `chain`, `tool`,
  `retriever`, ...) so the UI can render it appropriately.
- **LangChain calls are auto-traced**: once `LANGSMITH_TRACING=true`,
  `ChatGoogleGenerativeAI` (and other LangChain components) produce
  `"llm"` runs automatically, nested correctly alongside manual
  `@traceable` calls.
- **metadata**: arbitrary key/value data attached to one run.
- **tags**: short labels attached to one run, meant for filtering.

If anything here still feels unclear, ask before moving to Lesson 4.
