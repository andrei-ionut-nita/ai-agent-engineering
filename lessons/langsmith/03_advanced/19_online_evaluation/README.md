# Lesson 19: Scoring a sample of production runs after the fact

## What we're building

A script that pulls recent runs (Lesson 18's `list_runs`), samples a
fraction of them, judges each sampled one with a second model call, and
publishes the result as feedback (Lesson 17) directly on the original
run, no dataset, no `evaluate()`, just live traffic being scored after
the fact.

## What this reveals

Lessons 9-16 all evaluated against a fixed dataset, known questions,
known reference answers, run deliberately, on demand. Production
traffic is nothing like that: it's whatever real users actually send,
arriving continuously, with no reference answer to compare against.
**Online evaluation** is the practice of scoring that traffic anyway,
usually with an LLM-as-judge evaluator (since there's no ground truth to
check against mechanically) and usually on a **sample**, not everything,
because grading every single production run would mean doubling your
LLM costs for no benefit past a certain sample size.

LangSmith's UI has a built-in Rules feature that automates exactly this
pattern: define a filter (which runs qualify), a sample rate, and an
evaluator, and it runs continuously server-side, no script to schedule
or remember to re-run. This lesson builds the same logic by hand in
Python so the mechanism is visible: sample, judge, publish feedback,
each of them a concept already covered (Lessons 18, then a judge call
like Lesson 17's, then `create_feedback`, also Lesson 17's). A real Rule
in the UI is this same pipeline, running for you.

## The code, piece by piece

```python
recent_runs = list(client.list_runs(project_name=PROJECT_NAME, run_type="chain", limit=20))
```

Identical to Lesson 18, pulling whatever chain runs already exist to
stand in for "production traffic."

```python
sample = [run for run in recent_runs if random.random() < 0.3]
```

A crude 30% sample, in a real Rule this rate is configurable, and
usually much lower once traffic volume is high, sampling is what makes
online evaluation affordable at scale.

```python
score = judge_run(question, answer)
client.create_feedback(run_id=run.id, key="online_eval_reasonable", score=score, feedback_source_type="model")
```

The same `judge_run`-then-`create_feedback` shape as Lesson 17's
LLM-as-judge feedback, just applied to runs that already happened days
or minutes ago instead of one you just produced. `feedback_source_type="model"`
records that this score came from an automated judge, not a human, so
the UI can distinguish the two later.

## Running it

```bash
uv run python lessons/langsmith/03_advanced/19_online_evaluation/lesson.py
```

Run a few earlier lessons first if your project has little traffic in
it yet. You should see a handful of sampled runs printed with their
scores. In the UI, open one of those runs and confirm
`online_eval_reasonable` appears in its Feedback panel.

## Checkpoint

- **Online evaluation**: scoring live/production runs after the fact,
  as opposed to `evaluate()`'s deliberate runs against a fixed dataset.
- **Sampling**: scoring a fraction of traffic, not all of it, to keep
  evaluation cost proportional rather than doubling every request.
- **Rules (UI)**: LangSmith's built-in, server-side automation of this
  same sample-then-judge-then-feedback pipeline, no script required.

If anything here still feels unclear, ask before moving to Lesson 20.
