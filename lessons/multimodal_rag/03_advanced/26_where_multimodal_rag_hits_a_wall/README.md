# Lesson 26: Where Multimodal RAG Hits a Wall

## What we're building

No code today, this is the last lesson, and it's a bridge, not a
capstone. `lesson.py` prints a summary of specific limits this course
ran into along the way, each paired with where in this series (or in a
production system beyond it) that limit gets addressed. Nothing here is
new information, every limit was already demonstrated hands-on in an
earlier lesson; this just names them together, in one place, before
this course ends.

## Why this matters

This course committed to one implementation choice in Lesson 1,
captioning-then-embed, on purpose, and spent every lesson since
building out its consequences, good (reuses the existing pipeline,
inspectable captions) and bad (lossy summaries, a per-image vision cost
at generation time). A student who only remembers "multimodal RAG means
captioning images" missed half of Lesson 1; a student who can also name
what captioning costs, and what joint embedding spaces trade instead,
actually understands the choice this course made rather than having
memorized its outcome.

## Running it

```bash
uv run python lessons/multimodal_rag/03_advanced/26_where_multimodal_rag_hits_a_wall/lesson.py
```

## Expected output

Four limitations, each with the lesson that demonstrated it and what
addresses it: caption lossiness (Lesson 15, addressed by joint
embedding spaces, a different approach this course named but didn't
build, in Lesson 1), per-query re-captioning cost at scale (Lesson 19,
addressed by caching generation answers, not just captions, out of
scope here), fixed retrieval depth regardless of question complexity
(this course always retrieved a fixed `k`, whatever the question
actually needed, addressed by Adaptive RAG, the next course in this
series), and one-shot retrieval with no ability to notice a bad match
and try again (addressed by Agentic RAG, referenced but not built in
this series' naive_rag Lesson 26 either).

## Where to go from here

Multimodal RAG extended `naive_rag`'s exact pipeline with one new idea,
captioning-then-embed, and every lesson since Lesson 1 built out that
idea's real consequences, not just its happy path. `Adaptive RAG` (this
series' next course) picks up the "fixed retrieval depth" thread
directly: this course's `ask(query, state, k)` always used a `k` chosen
in advance, Adaptive RAG decides `k`, or whether to retrieve at all,
per question. This course's `ingest()`/`ask()` (Lesson 22) is built to
slot into that course's routing layer without modification, exactly the
point of the shared `Strategy` protocol.

Congratulations on completing the course.
