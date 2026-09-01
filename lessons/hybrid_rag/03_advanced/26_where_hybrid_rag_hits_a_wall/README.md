# Lesson 26: Where Hybrid RAG Hits a Wall

## What we're building

No code today, this is the last lesson, and it's a bridge, not a
capstone. `lesson.py` prints a summary of four specific limits this
course ran into along the way, each paired with the RAG architecture
later in this series built to address it. Nothing here is new
information, every limit was already demonstrated hands-on in an
earlier lesson; this just names them together, in one place, before this
course ends.

## Why this matters

`naive_rag`'s own bridge lesson predicted hybrid retrieval would fix
"retrieval that's confidently wrong." This course built that fix, RRF
fusion, and then, in Lesson 16, found a case where fusion itself is
still confidently wrong, a question whose own premise doesn't match its
answer, defeating dense and sparse independently, for different reasons,
with nothing to catch either failure. That's not a contradiction of
`naive_rag`'s prediction, hybrid retrieval genuinely does fix the two
specific failures Lesson 6 demonstrated (a bare ID, a paraphrase). It's
a reminder that "combining two things that each work most of the time"
doesn't produce something that works all of the time, it produces
something with a smaller, differently-shaped set of remaining failures.
This lesson names that remaining set honestly, the same way `naive_rag`'s
did.

## Running it

```bash
uv run python lessons/hybrid_rag/03_advanced/26_where_hybrid_rag_hits_a_wall/lesson.py
```

## Expected output

Four limitations, each with the lesson that demonstrated it and the
architecture that addresses it: fusion with nothing left to fuse
(Corrective RAG), no relevance threshold on the fused result (also
Corrective RAG), no multi-hop reasoning (Graph RAG, this series' next
course), and fixed retrieval depth regardless of question difficulty
(Agentic RAG).

## Where to go from here

Hybrid RAG doesn't replace Naive RAG, it adds a second retrieval
mechanism alongside the first and a way to combine their opinions. Graph
RAG (this series' next course) keeps both of those mechanisms and adds a
third kind of structure entirely, explicit relationships between facts,
for the specific multi-hop failure this course's Lesson 16 traced back
to "fusion can't gather what neither retriever found in one place."
Corrective, Agentic, Multimodal, and Adaptive RAG each add one further
capability on top of what this course and `naive_rag` already built,
not a fresh start.

Congratulations on completing the course.
