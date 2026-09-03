# Lesson 26: Where Graph RAG Hits a Wall

## What we're building

No new retrieval code today, this is the last lesson, and it's a
bridge, not a capstone. `lesson.py` prints a summary of five specific
limits this course ran into along the way, each paired with the RAG
architecture later in this series built to address it. Nothing here is
new information, every limit was already demonstrated hands-on in an
earlier lesson; this just names them together, in one place, before
this course ends.

## Why this matters

This course took Graph RAG, the second architecture in this series'
map, and built it by hand, which meant actually *hitting* its limits
rather than just reading about them: Lesson 16's corrupted graph
genuinely produced a degraded answer, silently, with no error anywhere
in the code. Lesson 19's timing genuinely showed quadratic cost. That
hands-on failure is worth more than an abstract description of "Graph
RAG has limitations," because you've now watched each one happen on
purpose, with your own code, against fixtures you can read yourself.

## Running it

```bash
uv run python lessons/graph_rag/03_advanced/26_where_graph_rag_hits_a_wall/lesson.py
```

## Expected output

Five limitations, each with the lesson that demonstrated it and the
architecture that addresses it: silently compounding extraction errors
(Corrective RAG), no confidence check before answering (Corrective
RAG), fixed traversal depth regardless of question complexity (Adaptive
RAG), one-shot traversal with no re-attempt (Agentic RAG), and graphs
that only ever model text (Multimodal RAG).

## Where to go from here

Graph RAG solved a real problem Naive RAG couldn't: multi-hop questions
whose answer lives in a relationship, not a single passage. It also
introduced a new failure this series hasn't confronted head-on yet,
retrieval (in this course's case, traversal) that runs, produces
well-formed output, and is simply wrong, with nothing in the pipeline
noticing. **Corrective RAG**, this series' next course, is built
specifically for that gap: it grades what got retrieved *before*
generation ever sees it, and corrects course, refining the query,
falling back to a different source, when the grade comes back low.
Lesson 16's corrupted-graph demonstration in this course is exactly the
kind of failure a grading step would have caught, if this course's
pipeline had one. It doesn't, yet, that's the whole reason Corrective
RAG exists.

Congratulations on completing the course.
