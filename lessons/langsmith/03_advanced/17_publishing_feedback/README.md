# Lesson 17: Attaching feedback to a run after it's already finished

## What we're building

One `rag_answer` call, given a pre-generated run id so it can be
identified afterward, then two pieces of feedback attached to that
exact run after it's done: a simulated user thumbs-up, and an
LLM-as-judge helpfulness score computed by a second model call.

## What this reveals

Every evaluator so far (Lessons 10-12) scored runs produced *by*
`evaluate()`, inside a controlled experiment, on a fixed dataset. Feedback
is different: it's a score attached to a run that already happened,
often in production, often well after the run finished, sometimes
seconds later (a user clicking a button), sometimes minutes later (a
batch job scoring yesterday's traffic). `create_feedback` is the
mechanism for that: given a run's id and a score, it attaches the score
to that run, wherever and whenever it ran.

This requires knowing the run's id ahead of time. `langsmith_extra={"run_id":
...}` lets you generate that id yourself, before calling the traced
function, specifically so you have something to hand to
`create_feedback` afterward. Without this, you'd need to search for the
run by other means (Lesson 18 covers querying/filtering runs, one way to
find a run id you didn't capture up front).

The two feedback calls here differ only in where the score came from,
not in how it's published: `user_thumbs_up` stands in for a real user's
click, `llm_judged_helpfulness` comes from asking a second model to
judge the first model's answer. Both use the exact same
`create_feedback` call underneath, feedback doesn't care whether a human
or a model produced the score.

## The code, piece by piece

```python
run_id = str(uuid.uuid4())
answer = rag_answer(question, langsmith_extra={"run_id": run_id})
```

Generates the run's id before it exists, then forces `rag_answer`'s run
to use that specific id via `langsmith_extra`, the same call-time kwarg
seen in Lesson 5, here carrying `run_id` instead of `metadata`.

```python
client.create_feedback(run_id=run_id, key="user_thumbs_up", score=1, comment="...")
```

Attaches a score to that exact run. `key` names the feedback metric
(shown as its own column in the UI, same idea as an evaluator's `"key"`),
`score` is the value, `comment` is optional free text.

```python
helpfulness = judge_helpfulness(question, answer)
client.create_feedback(run_id=run_id, key="llm_judged_helpfulness", score=helpfulness)
```

`judge_helpfulness` is its own traced run (visible separately in the
UI), but the feedback it produces is attached back to the *original*
`rag_answer` run, not to itself, that's the point: judging happens
elsewhere, feedback lands on the run being judged.

## Running it

```bash
uv run python lessons/langsmith/03_advanced/17_publishing_feedback/lesson.py
```

In the UI, find the `rag_answer` run for this question and open its
Feedback panel, both `user_thumbs_up` and `llm_judged_helpfulness`
should appear attached to it.

## Checkpoint

- **Feedback**: a score attached to a run after the fact, independent
  of experiments/datasets, the mechanism for production monitoring.
- **`langsmith_extra={"run_id": ...}`**: pre-assigns a run's id so it
  can be referenced later, e.g. to attach feedback.
- **`client.create_feedback(run_id, key, score, comment=...)`**:
  attaches one piece of feedback to one run.
- **Feedback source is orthogonal to the mechanism**: user clicks and
  LLM-as-judge scores both publish through the same call.

If anything here still feels unclear, ask before moving to Lesson 18.
