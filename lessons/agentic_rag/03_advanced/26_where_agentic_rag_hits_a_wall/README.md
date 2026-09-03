# Lesson 26: Where Agentic RAG Hits a Wall

## What we're building

No code today, this is the last lesson, and it's a bridge, not a
capstone. `lesson.py` prints a summary of four specific limits this
course ran into along the way, each paired with what, if anything,
later addresses it. Nothing here is new information, every limit was
already demonstrated hands-on in an earlier lesson; this just names
them together, in one place, before this course ends.

## Why this matters

This course's whole premise was letting the model decide, per
question, whether to retrieve, how many times, and what else to call
instead, and every lesson after Lesson 9 made that decision genuinely
more capable: multi-step loops, decomposition, citations, bounded
iteration, error-safe dispatch, a registry that scales past two or
three tools. What none of that touched is *what the model is
retrieving from*. `search_notes()` never stopped being a search over
plain Markdown text, from Lesson 4 through Lesson 25. A more capable
decision about *when* to search doesn't change *what* a search can find.

## Running it

```bash
uv run python lessons/agentic_rag/03_advanced/26_where_agentic_rag_hits_a_wall/lesson.py
```

## Expected output

Four limitations, each with the lesson that demonstrated it and what
addresses it: text-only retrieval (Multimodal RAG, this series' next
course), tool-choice reliability resting on hand-written descriptions
(an open problem, not fully solved anywhere in this series), the cost
of model-controlled round trips (Adaptive RAG, later in this series),
and no memory of which past tool choices actually helped (outside this
series' current scope).

## Where to go from here

Agentic RAG is not a discarded idea once Multimodal RAG starts, it's
the mechanism Multimodal RAG's retrieval tools plug into: a model
deciding whether to call an image-search tool versus a text-search tool
is the exact same decision this course built, applied to a wider set of
tools. Understanding this course thoroughly, particularly Lesson 16's
three failure modes and Lesson 21's registry pattern, is what makes
Multimodal RAG's added tool types legible instead of a fresh set of
concepts to learn from zero.

Congratulations on completing the course.
