# Lesson 7: Beginner Checkpoint - Traced Multi-Step Pipeline

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
pipeline built entirely out of ideas from Lessons 1 through 6, combined
into one thing. If you can read `lesson.py` and explain why every
`@traceable`, `run_type`, tag, and `thread_id` is there, you've mastered
the Beginner tier. If any piece feels unfamiliar, revisit the lesson it
came from before continuing to Intermediate.

## What it does

Runs three product reviews through a pipeline (clean text, classify
sentiment with Gemini, count words), fully traced, with every review
in this run grouped into a single thread in the LangSmith UI.

## Where each piece came from

```python
@traceable(run_type="tool", tags=["beginner-checkpoint"])
def clean(text: str) -> str: ...

@traceable(run_type="tool", tags=["beginner-checkpoint"])
def word_count(text: str) -> int: ...
```
Lesson 3: `run_type="tool"` for small, deterministic helper functions,
plus a tag identifying this project's runs.

```python
@traceable(run_type="chain", tags=["beginner-checkpoint"])
def classify_sentiment(text: str, batch_id: str) -> str:
    response = model.invoke(text, config={"metadata": {"thread_id": batch_id}})
```
Lesson 3 again (`run_type="chain"` around an auto-traced Gemini call,
producing a nested `"llm"` run) and Lesson 5 (`thread_id` passed through
`config`, so this nested call's run also carries the batch's thread id).

```python
@traceable(run_type="chain", tags=["beginner-checkpoint"], metadata={"lesson": 7})
def process_review(review: str, batch_id: str) -> dict:
    cleaned = clean(review)
    return {"word_count": word_count(cleaned), "sentiment": classify_sentiment(cleaned, batch_id)}
```
Lesson 2: three separately traced functions called from inside
`process_review`, becoming its children in the run tree.

```python
batch_id = str(uuid.uuid4())
...
result = process_review(review, batch_id, langsmith_extra={"metadata": {"thread_id": batch_id}})
```
Lesson 5: one `batch_id` shared across all three calls to
`process_review` in this run, passed via `langsmith_extra` so all three
top-level runs (and everything nested under them) join the same thread.

## Running it

```bash
uv run python lessons/langsmith/01_beginner/07_beginner_checkpoint_project/lesson.py
```

You should see a sentiment and word count printed for each of the three
reviews. In the LangSmith UI, find the Threads view: all three
`process_review` runs from this script run should appear grouped
together, each expandable into its `clean` / `classify_sentiment`
(and its nested `llm` call) / `word_count` children.

## Try this yourself

Without looking anything up:

- Add a fourth review to the list, does it join the same thread with no
  other changes?
- Change one tag in `tags=["beginner-checkpoint"]` to something else on
  just `classify_sentiment`, can you find it later by filtering on that
  tag in the UI?
- Remove the `thread_id` from one call, and confirm that run now shows
  up outside the thread, on its own.

If you can make these changes confidently, you're ready for the
Intermediate tier, starting at Lesson 8.
