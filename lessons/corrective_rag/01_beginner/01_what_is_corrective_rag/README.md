# Lesson 1: What Is Corrective RAG, and What Gap Does It Close?

## Where we left off

`naive_rag` (course 1) built the baseline shape: chunk, embed, retrieve,
generate. That course's own Lesson 14 and Lesson 22 (`choosing_k_and_thresholds`,
`metadata_filtering_with_chromadb`) already showed the specific crack in
that shape: top-k retrieval always returns its `k` best-scoring chunks,
even when none of them are actually relevant, and generation has no way
to know the difference between "these chunks answer the question" and
"these chunks merely scored highest." A similarity *threshold* helps
when nothing scores high enough to be worth using, but it does nothing
for the harder case, a wrong chunk that scores high because it's
topically close, just not actually the right one. **Corrective RAG**
is a full architecture built to close exactly that gap.

## What Corrective RAG adds

Yan et al. 2024, ["Corrective Retrieval Augmented
Generation"](https://arxiv.org/abs/2401.15884) (arXiv:2401.15884),
proposes a **retrieval evaluator**: a lightweight model that grades each
retrieved chunk's confidence before generation ever sees it, into three
buckets:

- **Correct**: keep it, but refine it further (the paper decomposes the
  chunk into strips and recomposes only the relevant ones).
- **Ambiguous**: keep the refined version, but also treat this as a
  signal the retrieval might be incomplete.
- **Incorrect**: discard it, and fall back to an external knowledge
  source (the paper uses web search) instead of generating from it.

That's the whole idea: retrieval alone can't tell good matches from
plausible-looking bad ones, so add a step whose only job is grading
what came back, then act differently depending on the grade.

## Two simplifications this course makes, and where they're closed

Building the full paper on day one skips the parts that make each piece
legible on its own. This course makes two deliberate simplifications
early, both named here so they don't surprise you later if you read the
paper directly:

1. **Beginner's rewrite loop queries the same corpus.** Lessons 6-7
   handle a "nothing retrieved is relevant" grade by rephrasing the
   query and re-retrieving from the *same* internal document set. The
   paper's actual response to a low-confidence grade is external web
   search, a fundamentally different corpus. Lesson 22 (Advanced tier)
   builds that real branch, and is explicit that *it*, not the Beginner
   loop, is what "Corrective RAG" means in the literature.
2. **Beginner grades chunks as binary relevant / not-relevant.** Lesson
   3 asks Gemini for a single yes/no call per chunk. The paper's full
   three-way correct / ambiguous / incorrect confidence grade needs
   strip-level refinement to have anything useful to *do* with
   "ambiguous," which doesn't exist until Lessons 10-11. Lesson 12
   upgrades the binary grade to the real three-way bucket once that
   machinery is in place.

## The code, piece by piece

This lesson's `lesson.py` is deliberately small, it asks Gemini the
question this whole course is going to keep asking, with no context at
all, the same "prove the gap exists before building the fix" move
Lesson 1 of `naive_rag` made. `QUESTION` is chosen so that naive top-1
retrieval (proven with real embeddings in Lesson 2) confidently returns
the *wrong* fixture file, not just a low-scoring miss, that specific
failure shape is this course's entire premise.

## Running it

```bash
uv run python lessons/corrective_rag/01_beginner/01_what_is_corrective_rag/lesson.py
```

## Expected output

Gemini's exact wording varies each run, but the shape is:

```
Question: Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?

Gemini, with no context:
<a guess, or an "I don't know" - varies each run>

Naive RAG (course 1) would embed this question, ...

Corrective RAG (Yan et al. 2024, ...) adds exactly the step naive RAG is missing: ...

Two simplifications this course makes early on, closed later:
  1. Beginner's rewrite-and-re-retrieve loop (Lessons 6-7) queries the SAME internal corpus again. ...
  2. Beginner grades chunks as a binary relevant / not-relevant call (Lesson 3). ...
```

If instead you see an error, check the
[Troubleshooting section](../../../../README.md#troubleshooting) in
this project's root README.

## Checkpoint

- **Corrective RAG**: retrieval, plus a grading step (the retrieval
  evaluator) that scores each chunk's relevance before generation ever
  sees it, and acts differently depending on the grade.
- **The gap it closes**: naive RAG's top-k retrieval always returns its
  best-scoring chunks, even when the best-scoring chunk is topically
  close but factually wrong for the specific question.
- **Two named simplifications**: an internal rewrite loop standing in
  for external search (closed in Lesson 22), and a binary grade standing
  in for the paper's three-way confidence bucket (closed in Lesson 12).

If anything here still feels unclear, ask before moving to Lesson 2.
