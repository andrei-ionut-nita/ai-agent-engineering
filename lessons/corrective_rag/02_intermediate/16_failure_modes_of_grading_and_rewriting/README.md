# Lesson 16: Failure Modes - Grader/Generator Circularity

## Where we left off

Every lesson since Lesson 3 has treated grading as a reliable check on
retrieval: naive retrieval might confidently return the wrong chunk, but
grading catches it. That assumption has gone untested until now. This
lesson tests it, directly, with a constructed example, because the
grader in this course isn't an independent referee, it's the same model
family (Gemini) as the generator it's supposed to be checking.

## Why that's a problem, specifically

If a passage would fool the generator into a confident, wrong answer, it
can fool the grader into passing that exact passage through, for the
same underlying reason. Grading only ever asks "does this passage
directly address the question," it never asks "is this passage's claim
actually true," because there's no ground truth available to check
against at grading time, only the passage's own text, read by the same
kind of model that will later read it again to generate an answer. This
is the corrective-RAG-specific version of the exact failure `naive_rag`
demonstrated with retrieval alone: a confident, plausible-looking wrong
answer, going uncaught, because nothing in the pipeline is actually
independent of the thing that produced the wrong answer.

## The constructed example

```python
FABRICATED_PASSAGE = (
    "According to Project Aurora's build log, the wind speed sensor's "
    "official manufacturer spec sheet calls for re-oiling every three "
    "days without exception, a maintenance interval the project has "
    "followed closely since the sensor was installed."
)
```

This passage directly contradicts the real fixture file's answer
("every few months"). It isn't a bad chunk, structurally, it's
confident, on-topic, well-formed, and directly addresses the question.
That's exactly the point: nothing about how it's written distinguishes
it from a real, correct passage, from the grader's perspective, or the
generator's.

## Running it

```bash
uv run python lessons/corrective_rag/02_intermediate/16_failure_modes_of_grading_and_rewriting/lesson.py
```

## Expected output

```
Q: How often does Project Aurora's wind speed sensor need re-oiling?

Real passage (weather-station.md):
  Grade: correct
  Generated answer: Based on the provided context, the wind speed sensor needs re-oiling every few months.

Fabricated passage (constructed for this lesson, contradicts the real one):
  '...calls for re-oiling every three days without exception...'

  Grade: correct
  Generated answer: Based on the provided context, the wind speed sensor needs re-oiling every three days without exception.

This is grader/generator circularity, demonstrated, not asserted: ...
```

Both passages get graded `correct`. Both generated answers are equally
confident. One of them is true and one of them is fabricated, and
nothing in this pipeline, as built through Lesson 15, can tell the
difference. That's not a bug in this course's specific prompts, it's a
structural limit of using one model family to grade its own inputs.

## Other failure modes, briefly

Two more, worth naming even though circularity is this lesson's main
subject:

- **Rewrite loops that don't converge**: Lesson 6-7's rewrite can, in
  principle, produce a new wording that still grades not-relevant,
  repeatedly, with no guarantee of eventually succeeding. Lesson 21
  bounds this with a max-attempts guard.
- **Strip-level over-fragmentation**: splitting a chunk too finely
  (Lesson 10) can separate a claim from the context that qualifies it,
  a strip like "every three days" read alone loses the surrounding
  sentence that might have revealed it was a superseded estimate, had
  one existed. Fine-grained grading isn't free of its own version of
  this lesson's problem.

## Checkpoint

- **Grader/generator circularity**: the retrieval evaluator shares the
  generator's model family, and therefore some of its blind spots,
  "grading fixes retrieval" is an assumption, not a guarantee.
- A passage doesn't need to look wrong to fool both grading and
  generation the same way, it can be confident, well-formed, and
  directly on-topic, and still be false, with nothing in this course's
  pipeline able to catch that.
- This is the specific limit Lesson 17 has to account for when
  interpreting a precision@k improvement, a higher score means
  retrieval found a more topically-relevant chunk, it does not mean the
  chunk's content was verified true.

If anything here still feels unclear, ask before moving to Lesson 17.
