# Lesson 22 (Optional): Corrective Grading as a Tool

## Where we left off

This lesson is optional, a cross-reference, not a hard dependency. It
doesn't require [`lessons/corrective_rag`](../../../corrective_rag/README.md)
to exist or be completed, but if you've done that course, this lesson
will feel immediately familiar: it's the same relevance-grading idea,
wired in as a fourth *tool* rather than a fixed pipeline stage.

## The idea being cross-referenced

[corrective_rag Lesson 3](../../../corrective_rag/01_beginner/03_grading_a_retrieved_chunk/README.md)
introduces `grade_chunk()`: ask Gemini a second, independent question,
"does this specific passage actually answer this specific question?",
because a high similarity score and a wrong retrieval can both be true
at once. That course makes grading a mandatory step every retrieval
goes through. This lesson asks a different question: what if grading
were just another tool the agent could reach for, the same way it
reaches for `search_notes` or `calculate`, only when it judges it's
actually needed?

## The code, piece by piece

```python
GRADE_PROMPT = """You are grading whether a retrieved passage is relevant \
enough to help answer a question. ..."""

def grade_passage(question: str, passage: str) -> str:
    ...
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"
```

This is `corrective_rag` Lesson 3's `grade_chunk()`, reimplemented
self-contained here (not imported, so this course has no dependency on
that one), same binary relevant/not_relevant judgment, same prompt
structure.

```python
"grade_passage": Tool(
    declaration=types.FunctionDeclaration(
        name="grade_passage",
        description=(
            "Check whether a passage you already retrieved with search_notes "
            "is actually relevant to a question. ... Use this when you're "
            "unsure a retrieved passage really answers the question before "
            "relying on it."
        ),
        ...
    ),
    fn=grade_passage,
),
```

Added to the same registry Lesson 21 built, no special-casing needed,
this is exactly what the registry pattern was for: a fourth tool is
one more dict entry.

```python
SYSTEM_INSTRUCTION = """... After calling search_notes, if you are not
confident the returned passage actually answers the question, call
grade_passage to check before relying on it. ..."""
```

Unlike `corrective_rag`'s mandatory grading, this instruction only
*suggests* grading when the agent isn't confident, it stays the
model's judgment call, not a step that always runs, the same "the
model decides" thesis this entire course has followed since Lesson 1,
now applied to correction itself, not just retrieval.

## Why agentic and corrective aren't competing ideas

It's tempting to treat these as two different architectures solving the
same problem differently, and therefore in competition. They're not:
`corrective_rag` is a stronger guarantee (every retrieval gets graded,
no exceptions) at a fixed cost (every retrieval pays for a grading
call). This lesson's version is a weaker guarantee (grading happens
only when the model decides to bother) at a lower, variable cost. Which
one a real system needs depends entirely on how costly a wrong,
ungraded retrieval actually is for that system, agentic RAG's whole
premise is that this kind of cost/reliability tradeoff should be a
choice, not something baked into the pipeline's shape by default.

## Running it

```bash
uv run python lessons/agentic_rag/03_advanced/22_optional_corrective_grading_as_a_tool/lesson.py
```

## Expected output

```
Q: How often does the aquarium's filter sponge get rinsed?
A: The aquarium's filter sponge gets rinsed every other water change.
```

Whether `grade_passage` gets called at all depends on the model's own
confidence in this run, a clean, unambiguous question like this one
often gets answered without ever invoking it, exactly the intended
behavior: grading is available, not mandatory.

## Checkpoint

- `grade_passage()` is `corrective_rag` Lesson 3's `grade_chunk()`,
  reused as an idea, reimplemented self-contained.
- Adding it as a fourth tool required exactly one new registry entry,
  Lesson 21's structural payoff.
- Mandatory grading (`corrective_rag`) and optional, agent-chosen
  grading (here) are different points on a cost/reliability tradeoff,
  not competing architectures, choosing between them is itself an
  agentic-style decision.

If anything here still feels unclear, ask before moving to Lesson 23.
