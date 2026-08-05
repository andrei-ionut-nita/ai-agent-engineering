# Lesson 12: Comparing two experiments head to head

## What we're building

Two variants of the RAG app, `rag_answer_concise` (asks for one short
sentence) and `rag_answer_detailed` (asks for thorough coverage), each
run as its own experiment over the same dataset, then compared directly
against each other with a pairwise evaluator.

## What this reveals

Every evaluator so far (Lessons 10-11) scored a run against a fixed
reference answer, in isolation. Sometimes there is no clean reference,
or the real question is comparative: "is version A better than version
B", not "does A match some ground truth". **Pairwise evaluation**
answers that directly: given two (or more) runs of the *same example*
from *different experiments*, decide which one is preferred.

This is exactly the situation you're in whenever you change a prompt,
swap a model, or tweak retrieval and want to know if it actually helped.
Two separate experiments each have their own average scores, but a
pairwise comparison forces a direct, per-example verdict: for this
specific question, which answer would you rather have gotten?

## The code, piece by piece

```python
concise_results = evaluate(..., experiment_prefix="rag-concise")
detailed_results = evaluate(..., experiment_prefix="rag-detailed")
```

Two ordinary experiments, run exactly as in Lesson 9, one per app
variant. Each produces its own `experiment_name`.

```python
def prefers_shorter(runs: list[Run], example: Example) -> dict:
    lengths = {run.id: len(run.outputs["answer"].split()) if run.outputs else None for run in runs}
    ...
```

A pairwise evaluator's signature differs from both earlier evaluator
types: it receives `runs`, a list of the runs different experiments
produced *for the same example*, plus that `example` itself. It returns
a `"scores"` dict keyed by each run's id, here, 1.0 for whichever run has
the fewest words, 0.0 for the other, 0.5 (a tie) for any run whose
`outputs` came back `None`. That guard isn't defensive programming for
its own sake: `evaluate_comparative` runs immediately after both
experiments finish, and a run's outputs can occasionally still be
finishing their write server-side at that exact moment, an ordinary
eventual-consistency gap, not a bug, when a script queries data it just
finished writing.

(A real preference judgment would
more likely ask an LLM which answer is more helpful, this lesson keeps
it mechanical, same reasoning as Lesson 10's evaluators, to stay
deterministic and free of an extra model call.)

```python
evaluate_comparative(
    [concise_results.experiment_name, detailed_results.experiment_name],
    evaluators=[prefers_shorter],
)
```

`evaluate_comparative()` takes a list of already-run experiment names
(not a dataset or a target function, both experiments already exist)
and a list of pairwise evaluators. It runs each evaluator once per
example, across the matching runs from every named experiment.

## Running it

```bash
uv run python lessons/langsmith/02_intermediate/12_pairwise_experiments/lesson.py
```

In the UI, open either experiment; a comparison view links to the other
one, showing, per question, which answer `prefers_shorter` favored.

## Checkpoint

- **Pairwise evaluation**: judging which of several runs *for the same
  example* is better, rather than scoring one run against a fixed
  reference.
- **Pairwise evaluator signature**: `(runs, example) -> {"key": ...,
  "scores": {run_id: score, ...}}`.
- **`evaluate_comparative()`**: runs pairwise evaluators across two or
  more already-completed experiments over the same dataset.

If anything here still feels unclear, ask before moving to Lesson 13.
