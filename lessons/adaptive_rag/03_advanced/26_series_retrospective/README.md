# Lesson 26: Series Retrospective

## What we're building

No code today. This is the last lesson of the last course in the
series, so it's not a bridge to anything, it's a retrospective.
`lesson.py` prints a walk through all seven courses in order: what each
one added, the specific limitation that addition ran into, and which
later course (or, for this course, nothing) picked that limitation up.
Nothing here is new information. Every fact below was already
demonstrated hands-on in an earlier lesson, in some cases an earlier
course. This just names the whole chain together, once, before the
series ends.

## Why this matters

The [rag-fundamentals](https://andreinita.co/learning/rag-fundamentals/)
course mapped nine RAG architectures in prose, as a conceptual survey,
before any of this series existed. Lesson 2 of this course opened with
almost the same map, but by then you'd already built six of those
architectures by hand and watched each one fail in a specific,
reproducible way: naive retrieval missing a multi-hop answer, hybrid
fusion with nothing left to fuse, a graph traversal that was
confidently wrong, corrective grading sharing a blind spot with the
model it was checking, an agent choosing a tool for the wrong reason,
a caption losing the one detail a question needed. This course's whole
premise, that no single strategy is always right, only means something
once you've personally watched five specific strategies each be wrong
in a different, specific way. That's what this lesson is for: putting
the whole chain in one place, now that you've earned it.

## Running it

```bash
uv run python lessons/adaptive_rag/03_advanced/26_series_retrospective/lesson.py
```

## Expected output

Seven courses, each with what it added, the limitation that addition
ran into, and where that limitation went next: Naive RAG (chunk, embed,
retrieve, generate, limited to one similarity search per question) into
Hybrid RAG's dense-plus-sparse fusion (limited to whatever both
retrievers found, together, in one place) into Graph RAG's explicit
relationships (limited to traversal that could be well-formed and still
wrong) into Corrective RAG's grading step (limited to one fixed
correction ladder run identically every time) into Agentic RAG's
model-chosen tool calls (limited to text) into Multimodal RAG's
captioning-then-embed pipeline (limited to a fixed retrieval depth
regardless of question difficulty) into this course's per-question
routing, which is where the chain ends, not because routing has no
limits of its own, but because addressing them is future work beyond
this series rather than a course already sitting in this repo.

## Where to go from here

Every architecture in this series solved a real problem the one before
it ran into on purpose, not a hypothetical one, and this course's
Lesson 21 is the proof: five of those six prior implementations plug
into this course's router without modification, because they all
already share the same `ingest() -> State` / `ask(query, state, k) ->
str` shape. That only works because each course was honest about its
own limits in its own closing lesson instead of overselling itself, so
the next course always knew exactly what problem it existed to solve.

This course has its own honest limit, and Lesson 17 already named it
rather than burying it: the routing rules this course tunes and the
mixed question set this course evaluates against are the same set,
which is train/test contamination, not a clean result. A router that
looks good on the question set it was tuned against is not the same
claim as a router that generalizes, and closing this series without
saying that plainly would repeat the exact mistake this series' whole
Corrective RAG course exists to catch: a well-formed answer that sounds
sure of itself and hasn't actually been checked.

If you've built all seven courses in order, you now know, hands-on,
what [rag-fundamentals](https://andreinita.co/learning/rag-fundamentals/)
could only describe: not which single RAG architecture is best, but
which specific failure each one is for. That's the whole series in one
sentence, and it's a better answer than the one you'd have given before
Lesson 1 of Naive RAG.

Congratulations on completing the series.
