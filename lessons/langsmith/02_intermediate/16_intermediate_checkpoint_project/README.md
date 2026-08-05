# Lesson 16: Intermediate Checkpoint - Dataset + Evaluator for the RAG App

## What this is

No new concepts in this lesson. This is a checkpoint: the RAG app,
dataset, prompt, and evaluators from Lessons 8-15, combined into one
full evaluation run. If you can read `lesson.py` and explain why every
piece is there, you've mastered the Intermediate tier. If any piece
feels unfamiliar, revisit the lesson it came from before continuing to
Advanced.

## What it does

Pulls the current prompt from the hub, answers every question in the
dataset with it, scores each answer two ways and the experiment as a
whole one more way, then reads the full results back into Python as a
table.

## Where each piece came from

```python
@traceable(run_type="retriever")
def retrieve(question: str) -> list[str]: ...
```
Lesson 8: the small in-memory RAG app's retrieval step.

```python
prompt = client.pull_prompt(PROMPT_NAME)
context = "\n".join(retrieve(question))
response = (prompt | model).invoke({"context": context, "question": question})
```
Lesson 13: pulling the versioned prompt from the hub rather than
hardcoding it, so any edits made there (Lesson 14) are picked up
automatically.

```python
def target(inputs: dict) -> dict:
    return {"answer": rag_answer(inputs["question"])}
```
Lesson 9: the adapter `evaluate()` needs between the dataset's
`inputs`/`outputs` shape and the app's real function.

```python
def keyword_overlap(...): ...
def is_concise(...): ...
```
Lesson 10: two independent per-example evaluators, one correctness-ish,
one about verbosity.

```python
def pass_rate(runs: list[Run], examples: list[Example]) -> dict: ...
```
Lesson 11: a summary evaluator computing one experiment-wide number
from every run and example together.

```python
results = evaluate(
    target,
    data=DATASET_NAME,
    evaluators=[keyword_overlap, is_concise],
    summary_evaluators=[pass_rate],
    experiment_prefix="rag-checkpoint",
)
```
Lessons 9-11 combined: one `evaluate()` call driving the whole
experiment, per-example and summary evaluators both attached.

```python
dataframe = fetch_test_results_with_retry(results.experiment_name, "feedback.keyword_overlap")
```
Lesson 15: pulling the finished experiment back as a `DataFrame` for a
quick local report, instead of only viewing it in the UI, retrying
until the feedback column is actually present, since per-run feedback
can finish indexing slightly after `evaluate()` returns.

## Running it

```bash
uv run python lessons/langsmith/02_intermediate/16_intermediate_checkpoint_project/lesson.py
```

You should see a table of questions, answers, and per-question scores,
followed by the average `keyword_overlap` across the whole dataset. In
the UI, the same experiment appears under `langsmith-course-rag-qa`,
alongside every experiment from earlier lessons.

## Try this yourself

Without looking anything up:

- Add a fourth evaluator of your own, say, one checking the answer
  doesn't repeat the question verbatim.
- Change the dataframe's printed columns to include `feedback.is_concise`
  broken out separately, and compute its pass rate the same way
  `keyword_overlap`'s average was computed.
- Push a new prompt version to the hub, re-run this lesson, and compare
  the new experiment's `pass_rate` to the previous one's, is your change
  actually an improvement?

If you can make these changes confidently, you're ready for the
Advanced tier, starting at Lesson 17.
