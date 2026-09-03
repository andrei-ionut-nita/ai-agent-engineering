# Lesson 17: Minimal Evaluation, Retrieve or Not

## Where we left off

Every earlier lesson judged the agent's decision to retrieve (or not)
by eyeballing one or two questions and deciding "yes, that looks
right." This lesson replaces eyeballing with a small, repeatable score,
the same idea as [naive_rag Lesson 17](../../../naive_rag/02_intermediate/17_minimal_evaluation_precision_at_k/README.md)'s
precision@k, applied to a different question: not "did retrieval find
the right document," but **"did the agent correctly decide whether to
retrieve at all?"**

## The code, piece by piece

```python
LABELED_QUESTIONS = [
    ("How often does the sourdough starter need feeding at room temperature?", True),
    ...
    ("What's 12 times 12?", False),
]
```

The label here isn't a source file (as in `naive_rag`'s precision@k),
it's a boolean: should this specific question trigger a `search_notes`
call to be answered correctly? Three questions genuinely need a
fixture note, three are answerable from general knowledge alone.

```python
def contents_have_tool_call(contents: list[types.Content]) -> bool:
    return any(part.function_call is not None for content in contents for part in (content.parts or []))
```

Rather than track a separate boolean flag through the loop, this
inspects the finished `contents` transcript directly: did any turn
contain a `function_call` part? That's a direct, structural answer to
"did retrieval happen," reading it straight out of the same object
Lesson 12 and 13 already established as the source of truth for what
actually happened in a conversation.

```python
hit = did_retrieve == should_retrieve
```

Unlike precision@k, this metric penalizes *both* directions of
mistake equally: retrieving when it wasn't needed (this lesson's
Lesson 16 "unnecessary retrieval" failure) and skipping retrieval when
it was needed (a Lesson 6-style false negative). Both count as a miss.

## Why this doesn't generalize (yet)

[naive_rag Lesson 17's "Why this doesn't generalize (yet)" section](../../../naive_rag/02_intermediate/17_minimal_evaluation_precision_at_k/README.md#why-this-doesnt-generalize-yet)
applies here without needing to be rederived: six labeled questions is
enough to demonstrate the *mechanism* of this metric, not enough to
trust the resulting number. A single flipped decision swings this score
by roughly 17 points (1/6), and the same tune/eval contamination trap
applies just as directly, if `SEARCH_NOTES_DECLARATION`'s description
were iteratively tweaked until it scored 1.00 on these exact six
questions, that score would stop measuring anything beyond how well the
description fits this specific, tiny set.

## Running it

```bash
uv run python lessons/agentic_rag/02_intermediate/17_minimal_evaluation_retrieve_or_not/lesson.py
```

## Expected output

```
Retrieve-or-not evaluation:
  [HIT ] 'How often does the sourdough starter need feeding at room temperature?' -> expected retrieve=True, got retrieve=True
  [HIT ] 'How is the vinyl collection organized on the shelves?' -> expected retrieve=True, got retrieve=True
  [HIT ] 'What's the signal chain order on the guitar pedalboard?' -> expected retrieve=True, got retrieve=True
  [HIT ] 'What is the chemical symbol for gold?' -> expected retrieve=False, got retrieve=False
  [HIT ] "What's the capital of Japan?" -> expected retrieve=False, got retrieve=False
  [HIT ] "What's 12 times 12?" -> expected retrieve=False, got retrieve=False

  Accuracy: 1.00 (6/6)
```

A perfect score reflects this course's small, clearly-scoped tool
description and clean question set, not a claim that retrieve-or-not
decisions are generally this reliable, Lesson 16's ambiguous-question
demo already showed a case where the same decision goes wrong.

## Checkpoint

- This metric scores a *decision* (retrieve or not), not an *answer*,
  reading it directly out of the `contents` transcript's structure.
- It penalizes over-retrieval and under-retrieval equally, both are
  real failures, in opposite directions.
- Same generalization caveat as `naive_rag` Lesson 17: a handful of
  labeled questions demonstrates the mechanism, not a trustworthy
  number, and tuning the tool description against this exact set would
  invalidate the score the same way tuning a similarity threshold
  against it did there.

If anything here still feels unclear, ask before moving to Lesson 18.
