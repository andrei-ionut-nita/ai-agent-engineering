# Lesson 20: Failing a build when an experiment's score regresses

## What we're building

The same RAG experiment and `pass_rate` summary evaluator from Lesson
11, run once, its aggregate score read back, compared against a fixed
`BASELINE_PASS_RATE`, and the script exits with a non-zero status code
if the score falls short, exactly the signal a CI system uses to fail a
build.

## What this reveals

Every experiment so far ended with you reading a score and deciding for
yourself whether it looked fine. In a real project, that decision needs
to happen automatically, on every pull request, without a human staring
at a dashboard each time. **Regression testing** is running the exact
same evaluation Lessons 9-16 already built, but as an automated gate:
if the score drops below some agreed baseline, the build fails, the same
way a failing unit test blocks a merge.

`BASELINE_PASS_RATE` here is a stand-in for what would really be a
number checked into the repo (a config value, a constant like this one,
or a file read at the start of the script), representing "the lowest
this metric is allowed to be." Raising that number is itself a
deliberate decision, made when a real improvement lands, not something
this script does on its own.

## The code, piece by piece

```python
results = evaluate(target, data=DATASET_NAME, summary_evaluators=[pass_rate], experiment_prefix="rag-ci-check")
```

The same `evaluate()` call, and the same `pass_rate` summary evaluator,
from Lesson 11.

```python
project = client.read_project(project_name=results.experiment_name)
summary_feedback = list(client.list_feedback(sessions=[str(project.id)], feedback_key=["pass_rate"]))
current_score = summary_feedback[0].score
```

An experiment is stored internally as a "project," `read_project` reads
it back to get its id. Per-example evaluator scores (like Lesson 10's
`keyword_overlap`) attach to individual runs, and average out on
`project.feedback_stats`. Summary evaluator scores are different: they
attach to the experiment itself, with no individual run behind them
(their feedback's `run_id` is `None`), so they never show up in
`feedback_stats`. `list_feedback`, scoped to the experiment's session id
and the evaluator's key, is how you read a summary evaluator's own
score back, exactly the `pass_rate` number computed during
`evaluate()`, now available in Python to act on.

```python
if current_score < BASELINE_PASS_RATE:
    print("REGRESSION: ...")
    sys.exit(1)
```

`sys.exit(1)` is what makes this a real gate rather than just a printed
warning: any CI system (GitHub Actions, GitLab CI, anything that runs
shell commands) treats a non-zero exit code as a failed step, blocking
the pipeline exactly like a failing test would.

## Running it

```bash
uv run python lessons/langsmith/03_advanced/20_regression_testing_in_ci/lesson.py
```

Then, to see it actually fail: temporarily change `retrieve()` to always
`return []`, breaking the app's ability to answer correctly, and run it
again. You should see the `pass_rate` drop and the script exit non-zero
(check with `echo $?` after it runs).

## Checkpoint

- **Regression testing**: automatically comparing a fresh experiment's
  score against a baseline, instead of a human reviewing it manually.
- **`client.read_project(project_name=...)`**: reads an experiment
  (internally a "project") back, including `feedback_stats` for every
  attached feedback/evaluator key.
- **`sys.exit(1)`**: the mechanism that turns a Python script's result
  into a CI-recognizable pass/fail signal.

If anything here still feels unclear, ask before moving to Lesson 21.
