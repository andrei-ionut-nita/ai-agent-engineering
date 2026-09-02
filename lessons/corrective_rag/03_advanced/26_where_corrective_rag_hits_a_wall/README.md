# Lesson 26: Where Corrective RAG Hits a Wall

## What we're building

No code today, this is the last lesson, and it's a bridge, not a
capstone. `lesson.py` prints a summary of four specific limits this
course ran into along the way, each paired with the lesson that
demonstrated it and what addresses it next. Nothing here is new
information, every limit was already shown hands-on in an earlier
lesson; this just names them together, in one place, before this course
ends.

## Why this matters

`naive_rag` Lesson 26 named Corrective RAG as the fix for naive
retrieval's confidently-wrong top-k chunk, and this course built that
fix, by hand, and actually watched it work (Lesson 17's precision@k
jump from 0.80 to 1.00) and actually watched it have limits (Lesson 16's
circularity demo, Lesson 21's bounded loop). That's worth more than an
abstract description of "Corrective RAG has limitations," because
you've now built the mechanism, tested its assumption, and found the
real edge.

## Running it

```bash
uv run python lessons/corrective_rag/03_advanced/26_where_corrective_rag_hits_a_wall/lesson.py
```

## Expected output

Four limitations, each with the lesson that demonstrated it: grading's
shared blind spot with generation (Lesson 16), bounded correction that
can still honestly fail (Lesson 21), a fixed correction strategy applied
identically to every question (Lessons 6-7, 14, 22), and one retrieval
pass, corrected, being still just one pass (Lessons 8-9).

## Where to go from here

Corrective RAG is a real improvement over naive RAG, not a discarded
attempt, this course's Lesson 17 numbers prove that directly. Agentic
RAG (this series' next course) is what addresses this course's last two
limits: instead of a fixed correction ladder every question runs
through the same way, an agent decides, per question, what to do next,
including whether grading and correction are even the right tools to
reach for. This course's grading, filtering, rewriting, and external
search don't get thrown away there, they become capabilities an agent
can choose among, rather than a sequence every question runs through
identically.

Congratulations on completing the course.
