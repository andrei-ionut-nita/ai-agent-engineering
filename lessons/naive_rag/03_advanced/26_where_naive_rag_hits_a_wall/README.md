# Lesson 26: Where Naive RAG Hits a Wall

## What we're building

No code today, this is the last lesson, and it's a bridge, not a
capstone. `lesson.py` prints a summary of five specific limits this
course ran into along the way, each paired with the RAG architecture
later in this series built to address it. Nothing here is new
information, every limit was already demonstrated hands-on in an
earlier lesson; this just names them together, in one place, before
this course ends.

## Why this matters

The [rag-fundamentals](https://andreinita.co/learning/rag-fundamentals/)
course mapped nine RAG architectures in prose, as a conceptual survey.
This course took the simplest one, Naive RAG, and built it by hand,
which meant actually *hitting* its limits rather than just reading about
them: Lesson 16's multi-hop question genuinely failed with `k=1`.
Lesson 12's scoped search genuinely returned a confidently wrong answer.
That hands-on failure is worth more than an abstract description of
"Naive RAG has limitations," because you've now watched each one happen
on purpose, with your own code, against a document you can read
yourself.

Every architecture named below solves a real problem this specific
course ran into, not a hypothetical one.

## Running it

```bash
uv run python lessons/naive_rag/03_advanced/26_where_naive_rag_hits_a_wall/lesson.py
```

## Expected output

Five limitations, each with the lesson that demonstrated it and the
architecture that addresses it: multi-hop questions (Graph RAG),
confidently-wrong retrieval (Corrective RAG), one-shot retrieval
(Agentic RAG), text-only retrieval (Multimodal RAG), and fixed retrieval
depth regardless of question complexity (Adaptive RAG).

## Where to go from here

Naive RAG is the foundation every one of those architectures builds on,
not a discarded first draft. Hybrid RAG (this series' next course) adds
keyword search alongside the embedding-based search this course already
built; Graph, Corrective, Agentic, Multimodal, and Adaptive RAG each add
one specific capability on top of the same chunk-embed-retrieve-generate
shape this course started from. Understanding this course thoroughly,
rather than skimming it, is what makes every one of those additions
legible instead of magical.

Congratulations on completing the course.
