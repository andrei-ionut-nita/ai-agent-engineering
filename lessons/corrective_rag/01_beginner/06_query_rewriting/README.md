# Lesson 6: Query Rewriting

## Where we left off

Lesson 5's filtering fixed a case where the *right* chunk was retrieved
but outranked. That trick has a hard limit: if every retrieved chunk
grades not-relevant, filtering leaves you with an empty context, no
better than the naive answer. This lesson adds the other half of
Beginner-tier correction: when grading comes back all-negative,
rephrase the query itself and try again.

## A named simplification, up front

This is the internal rewrite loop Lesson 1 already named as a
simplification of the paper. Yan et al. 2024's actual response to a
low-confidence grade is external web search, a different knowledge
source entirely. Rewriting the query and searching the *same* internal
corpus again is the easier version to build first, and it's genuinely
useful for one specific failure mode (bad wording), but it cannot do
what real external search does (find an answer that was never in the
corpus). Lesson 22 builds that real branch.

## The code, piece by piece

```python
QUESTION = "What is the capital of France?"
```

Deliberately not a wording problem. None of the five fixture notes have
anything to do with France, this question is unanswerable from this
corpus no matter how it's phrased. That's the point: this lesson's job
is to show the rewrite *mechanism* honestly, including what it can't do.

```python
REWRITE_PROMPT = """The question below was just asked against a small \
personal notes collection (topics: a home weather station, a garden, a \
pizza dough recipe, a bookshelf, and cello practice), and none of the \
retrieved passages were relevant. Rewrite the question...
```

Telling the rewriter what topics the corpus actually covers (instead of
rewriting blind) gives it a real shot at fixing a wording mismatch, the
same idea as a human search user narrowing a query after a bad first
result. It's also, implicitly, information Gemini can use to notice a
question is off-topic entirely rather than off-topic due to wording.

## Running it

```bash
uv run python lessons/corrective_rag/01_beginner/06_query_rewriting/lesson.py
```

## Expected output

```
Q: What is the capital of France?

Top-3, graded:
  <three notes, scores roughly 0.42-0.50>: not_relevant
  ...

All graded not-relevant: True

Rewritten query: 'What is the capital of France?'
```

Gemini's rewrite is often the question unchanged (or trivially
reworded), it correctly recognizes there's no wording fix available
here, the question is off-topic for this corpus, not badly phrased.
That's the honest outcome for this specific example, and the README
text explains why. If you swap in a genuinely awkward but in-corpus
question of your own, you should see the rewrite actually change the
wording toward something closer to the fixtures' own vocabulary.

## Checkpoint

- **query rewriting**: prompting the model to rephrase a question when
  every retrieved chunk grades not-relevant, a repair aimed at *wording*
  problems specifically.
- What it can fix: a question phrased in vocabulary that doesn't match
  the corpus, even though the corpus contains the answer.
- What it can't fix: a question the corpus genuinely has no answer to,
  no rephrasing manufactures information that was never there. Lesson 22
  builds the paper's real fix for that case.

If anything here still feels unclear, ask before moving to Lesson 7.
