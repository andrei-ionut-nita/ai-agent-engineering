# Lesson 14: Query Rewriting Strategies

## Where we left off

Lessons 6-7 built one rewrite strategy: ask Gemini to rephrase a query
when everything graded not-relevant. That's one tool for one job. This
lesson names three distinct strategies, useful for different failure
shapes:

- **Broadening**: a question too specific to match a passage that
  discusses the same idea in more general terms.
- **Narrowing**: a question too vague to distinguish between passages,
  adding concrete, likely-relevant terms.
- **Decomposing**: a question that's actually two (or more) questions at
  once, split it, retrieve each part separately.

## Tuning signal, stated explicitly

Per this course's cross-course convention (see
`docs/RAG-SERIES-PLAN/README.md`'s eval-methodology note), any lesson
that tunes something needs to say plainly whether that tuning came from
a held-out signal or from the same labeled set Lesson 17 reports its
score against. **This lesson's heuristic is safe**: which strategy to
try for which failure shape (compound → decompose, vague → narrow,
over-specific → broaden) was chosen by inspecting the failure shapes
Lessons 6-12 already demonstrated by hand, not by sweeping strategies
against Lesson 17's five labeled questions and keeping whichever scored
best there. If it had been tuned that way, Lesson 17's score would be
measuring how well the heuristic was fit to the five questions it's also
graded on, not whether the heuristic actually generalizes.

## The code, piece by piece

```python
sub_questions = [
    line.strip() for line in call_model(DECOMPOSE_PROMPT.format(question=compound_question)).splitlines()
    if line.strip()
]
```

Decomposition, unlike the other two strategies, changes *how many*
queries get retrieved, one compound question becomes several simple
ones, each retrieved independently, then whatever downstream step needs
both answers (generation, usually) sees results from both.

## Running it

```bash
uv run python lessons/corrective_rag/02_intermediate/14_query_rewriting_strategies/lesson.py
```

## Expected output

```
Compound question: 'How long is the cello practice session, and what color-based system organizes the bookshelf?'
  combined query, k=2: cello-practice.md (score=0.7xxx)
  combined query, k=2: bookshelf.md (score=0.7xxx)

  Decomposed into: ['How long is the cello practice session?', 'What color-based system organizes the bookshelf?']
  sub-question 'How long is the cello practice session?' -> cello-practice.md (score=0.7xxx, higher)
  sub-question 'What color-based system organizes the bookshelf?' -> bookshelf.md (score=0.7xxx, higher)
```

On this course's small, five-document corpus, the combined query already
finds both correct sources, this corpus is too clean to force a miss.
What's still visible: each sub-question's own top score is noticeably
higher than the same source scored inside the blended combined query.
That gap is the whole mechanism, at real scale (thousands of chunks
instead of five), it's exactly what separates a combined query that
misses a source from a decomposed one that finds it.

## Checkpoint

- Three rewrite strategies for three different failure shapes:
  broadening, narrowing, decomposing.
- Decomposing a compound question and retrieving each part separately
  produces a stronger, less-averaged signal per source, even when a
  combined query already happens to work on a small corpus.
- This lesson's strategy-selection heuristic is tuned against Lessons
  6-12's hand-inspected failure shapes, a signal separate from Lesson
  17's labeled evaluation set, not against that set itself.

If anything here still feels unclear, ask before moving to Lesson 15.
