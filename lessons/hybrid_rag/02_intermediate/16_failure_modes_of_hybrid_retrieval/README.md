# Lesson 16: Failure Modes of Hybrid Retrieval

## Where we left off

Every earlier lesson's failures had a fix: dense missed an ID, sparse
caught it; sparse missed a paraphrase, dense caught it; fusion combined
both and recovered. This lesson shows the case fusion can't fix:
a question where *neither* retriever ranks the right document highly to
begin with.

## The code, piece by piece

```python
QUESTION = "What change finally made things work reliably again?"
EXPECTED = "old_travel_router.md"
```

This question presupposes its own answer shape: "a change fixed
something." `old_travel_router.md`'s actual resolution is the opposite,
it was deliberately kept on an *older* firmware build, specifically
because updating had introduced a bug. Nothing "changed" in the sense
the question assumes, the fix was refusing to change.

## Running it

```bash
uv run python lessons/hybrid_rag/02_intermediate/16_failure_modes_of_hybrid_retrieval/lesson.py
```

## Expected output

```
Question: 'What change finally made things work reliably again?'
Correct answer: old_travel_router.md

Dense ranking:  ['home_network.md', 'bike_maintenance.md', '3d_printer.md', 'espresso_machine.md', 'houseplants.md', 'old_travel_router.md']
  old_travel_router.md finished at rank 6 of 6

Sparse ranking: ['3d_printer.md', 'espresso_machine.md', 'home_network.md', 'houseplants.md', 'bike_maintenance.md', 'old_travel_router.md']
  old_travel_router.md finished at rank 6 of 6

Fused ranking:  ['home_network.md', '3d_printer.md', 'espresso_machine.md', 'bike_maintenance.md', 'houseplants.md', 'old_travel_router.md']
  old_travel_router.md finished at rank 6 of 6
```

Dead last, in every single ranking, including the fused one. Dense fails
because the query's *meaning* ("a change fixed it") points away from a
document whose actual point is "nothing changed." Sparse fails because
none of the query's words (`"change,"` `"work,"` `"reliably"`) are
distinctive enough to single this document out from five others that
all share the same "here's what fixed it" narrative shape. Fusion has
nothing to recover, when a document finishes last in both inputs, there
is no position left to fuse it up from, RRF only ever reorders what each
retriever already found, it can't surface something neither one found at
all.

## Why this matters more than it looks like

This isn't a corpus-size problem, more documents wouldn't fix a question
built on a wrong assumption about its own answer. It's a genuine ceiling
on what retrieval, dense, sparse, or fused, can do: retrieval finds
documents that match a query's words or meaning, it has no way to notice
when a query's *premise* is simply false for the document that actually
answers it. Fixing this needs something retrieval alone can't provide,
which is exactly the opening `corrective_rag` (course 4 in this series)
is built around: grading retrieved results and rewriting the query when
they don't hold up.

## Checkpoint

- Fusion recombines existing rankings, it can't invent a good rank for a
  document that both retrievers already ranked poorly.
- A query built on a wrong assumption about its own answer's shape can
  defeat both dense and sparse simultaneously, for different reasons,
  with no floor to catch it.
- This failure mode isn't fixed by anything in this course. It's a
  preview of why the series continues past Hybrid RAG at all.

If anything here still feels unclear, ask before moving to Lesson 17.
