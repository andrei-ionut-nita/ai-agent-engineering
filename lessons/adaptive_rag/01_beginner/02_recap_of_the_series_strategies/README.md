# Lesson 2: What the Series Built, and What Each Piece Is For

## Where we left off

Lesson 1 showed one specific failure: a fixed, single-document naive
strategy couldn't answer a question that needed two documents at once.
That's one failure, from one strategy. Before this course builds a
router, it's worth naming, plainly, what all five prior strategies in
this series are each good and bad at, so the routing rules Lessons 3
through 8 build aren't arbitrary, they're a direct response to specific,
already-demonstrated failure modes.

This lesson makes no new API call and adds no new mechanic. If you
completed the other five courses in this series, everything below is a
recap of things you already watched happen firsthand. If you haven't,
read this as a summary, then go build and watch each one fail yourself,
that's what actually makes the recap mean anything.

## The five strategies, good and bad

**Naive RAG**: good at single-fact lookup inside one document. Bad at
multi-hop questions (this failed at k=1 in `naive_rag`'s own Lesson 16),
and it can be confidently wrong on a scoped search instead of admitting
it doesn't know (`naive_rag` Lesson 12).

**Hybrid RAG**: good at fixing exactly two things naive retrieval alone
missed, a bare-ID lookup and a paraphrased query. Bad because fusion has
nothing left to fuse when neither retriever finds anything relevant,
there's no relevance threshold on the fused result, it's still
confidently wrong on a question whose own premise doesn't match its
answer (`hybrid_rag` Lesson 16), and it still has no multi-hop reasoning
of its own.

**Graph RAG**: good at multi-hop questions whose answer lives in a
relationship between two entities, not in any single passage. Bad
because a corrupted or degraded graph produces a well-formed but
silently wrong answer, with no error anywhere to catch it (`graph_rag`
Lesson 16), there's no confidence check before answering, traversal
depth is fixed regardless of how complex the question actually is, and
traversal cost grows quadratically as the corpus grows (`graph_rag`
Lesson 19).

**Corrective RAG**: good at catching and correcting a bad retrieval
before generation ever sees it, precision@k jumped from 0.80 to 1.00 in
`corrective_rag`'s own Lesson 17. Bad because grading shares a blind
spot with the model doing the grading (`corrective_rag` Lesson 16's
circularity demo), bounded correction can still honestly fail, a fixed
correction ladder runs identically for every question regardless of
whether that question needed correcting at all, and underneath it all
it's still just one retrieval pass, corrected.

**Agentic RAG**: good at letting the model decide, per question, whether
to retrieve, how many times, and what else to call. Bad because it never
changes WHAT is being searched, still text-only (`agentic_rag` Lesson
26), tool-choice reliability rests entirely on hand-written tool
descriptions, an unsolved problem, and model-controlled round trips cost
more, every extra call the model chooses to make is a real extra cost.

## The pattern across all five

Every strategy here was the right answer to a specific, already-observed
failure in the strategy before it, and every one of them then ran into
its own new failure. None of the five is always right. That's not a
weakness unique to any one of them, it's the actual shape of the
problem: different questions need different retrieval strategies, and
picking one strategy and running every question through it, no matter
how good that one strategy is, guarantees it'll be wrong for some
fraction of the questions it sees.

This course's whole premise follows directly from that: instead of
picking one of the five and living with its blind spot, classify a
question's complexity first, then route it to whichever of the five
strategies is actually suited to that complexity. Lessons 3 through 8
build exactly that, starting with the classifier.

## Running it

```bash
uv run python lessons/adaptive_rag/01_beginner/02_recap_of_the_series_strategies/lesson.py
```

## Expected output

The five strategies above, each with its "good at" and "bad at" points,
printed in order, followed by the one-paragraph statement of this
course's premise. No AI call happens in this lesson; the output is
identical every run.

## Checkpoint

- Naive, Hybrid, Graph, Corrective, and Agentic RAG each solved a real,
  specific problem the strategy before it had, and each then ran into
  its own new one.
- No single strategy from the series is always right, that's the
  motivating fact behind this entire course, not a rhetorical setup.
- Routing means matching a question's complexity to the strategy suited
  to it, not finding one "best" strategy to replace the other four.

If anything here still feels unclear, ask before moving to Lesson 3.
