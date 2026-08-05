# Lesson 8: A small RAG app, and a dataset of examples to test it against

## What we're building

A minimal retrieval-augmented-generation (RAG) app: `retrieve()` looks
up relevant text from a tiny in-memory knowledge base, `rag_answer()`
feeds that text to Gemini as context for answering a question. Then, a
**dataset** in LangSmith: a named collection of example
question/reference-answer pairs, uploaded once, that this app (and
later evaluators) can be run against repeatedly.

## Why a new app, and why a dataset

The calculator agent from the Beginner tier is great for tracing, but
it doesn't produce anything with an objectively "right answer" to
compare against, `12 * 5 = 60` either matches or it doesn't, there's no
room for an evaluator to demonstrate judgment. Question answering does:
"What is LangGraph used for?" has a few different acceptable phrasings,
which is exactly the kind of case evaluation (Lessons 9-12) is built
for.

A **dataset** is what makes repeatable evaluation possible at all.
Without one, "testing" an LLM app means running it by hand and eyeballing
the output. With one, you define a fixed set of inputs and (optionally)
reference outputs once, then every future change to the app, or to the
prompt, or to the model, can be re-run against the exact same set and
compared like-for-like.

## The code, piece by piece

```python
@traceable(run_type="retriever")
def retrieve(question: str) -> list[str]:
    matches = [text for key, text in DOCS.items() if key in question.lower()]
    return matches or list(DOCS.values())
```

A keyword-matching stand-in for a real vector-store retriever, `run_type`
and tracing behave identically to a real one (Lesson 3), the difference
is only in how the matching itself works.

```python
EXAMPLES = [
    {"inputs": {"question": "..."}, "outputs": {"answer": "..."}},
    ...
]
```

Each example is a plain dict with an `inputs` dict (whatever your app
needs as input, here just `question`) and an `outputs` dict (the
reference/expected result, here `answer`). This shape is exactly what
`evaluate()` in Lesson 9 expects to compare against.

```python
if client.has_dataset(dataset_name=DATASET_NAME):
    ...
    return
dataset = client.create_dataset(dataset_name=DATASET_NAME, description="...")
client.create_examples(dataset_id=dataset.id, examples=EXAMPLES)
```

`Client` is the SDK's general-purpose object for everything that isn't
just tracing a run, creating datasets, examples, and (later) reading
back experiment results. `has_dataset` avoids re-creating (and
erroring on) a dataset that already exists, so re-running this lesson
is safe.

## Running it

```bash
uv run python lessons/langsmith/02_intermediate/08_dataset_upload/lesson.py
```

In the UI, open the Datasets tab and find `langsmith-course-rag-qa`,
with the three examples above visible inside it.

## Checkpoint

- **Dataset**: a named, reusable collection of example inputs (and
  optionally reference outputs), stored in LangSmith.
- **Example**: one `{inputs, outputs}` pair inside a dataset.
- **`Client`**: the SDK object for dataset/example management (and, in
  later lessons, feedback and run queries), distinct from tracing
  functions like `@traceable`.
- **Why a dataset matters**: it turns "does this still work" from an
  eyeball check into a repeatable, comparable experiment.

If anything here still feels unclear, ask before moving to Lesson 9.
