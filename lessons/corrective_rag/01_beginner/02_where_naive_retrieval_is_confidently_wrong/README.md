# Lesson 2: Where Naive Retrieval Is Confidently Wrong

## Where we left off

Lesson 1 asked you to take on faith that naive top-1 retrieval can
confidently return the wrong chunk. This lesson proves it, with real
embeddings, on this course's own fixtures, the same "reproduce the
failure before fixing it" structure `naive_rag` used for its own
threshold and metadata-filtering lessons.

## The setup: two notes about the same project, different vocabulary

`fixtures/notes/weather-station.md` describes Project Aurora (a
Raspberry Pi weather station) in detail: sensors, a SQLite database, an
SD card, a daily cloud backup. It never says which room the Raspberry
Pi is actually in.

`fixtures/notes/bookshelf.md` mentions, almost in passing, that "Project
Aurora's Raspberry Pi lives... on a small shelf next to the bookshelf...
in the study." That's the actual answer to this lesson's question, but
it uses almost none of the weather-station vocabulary the question
itself is phrased in.

## The code, piece by piece

```python
QUESTION = (
    "Project Aurora's Raspberry Pi writes sensor readings to a SQLite "
    "file on its SD card. Where does that Raspberry Pi physically live "
    "in the house?"
)
```

The question is phrased using weather-station.md's own words (SQLite,
SD card, sensor readings) on purpose, this is exactly how a real user
would ask it, by describing what they already know about the project,
not by trying to game the retriever.

```python
top1 = retrieve(QUESTION, store, k=1)
```

Naive RAG's retrieval, unchanged from `naive_rag` Lesson 6: embed the
question, rank every chunk by cosine similarity, take the top 1. No
grading, no threshold, nothing corrective, this is the baseline.

```python
correct_chunk = next(record for record in store if record["source"] == CORRECT_SOURCE)
```

For comparison only, this pulls out `bookshelf.md` directly (not via
retrieval) so you can see what the *correct* chunk's own score was, and
what generation produces when it actually gets handed the right context.

## Running it

```bash
uv run python lessons/corrective_rag/01_beginner/02_where_naive_retrieval_is_confidently_wrong/lesson.py
```

## Expected output

```
Q: Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?

Naive top-1 retrieval:
  [WRONG] weather-station.md (score=0.7xxx)

Generated answer from that chunk:
The provided context does not contain the answer...

The correct source, bookshelf.md, scored 0.7xxx (ranked below weather-station.md, but well above every other note).
Generated answer from the CORRECT chunk:
Based on the provided context, Project Aurora's Raspberry Pi physically lives on a small shelf next to the bookshelf in the study.
```

The exact scores vary slightly between runs, but `weather-station.md`
should consistently outrank `bookshelf.md`, both comfortably above the
other three notes (roughly 0.55-0.60). This isn't a low-similarity
miss like `naive_rag` Lesson 14's "capital of France" example, both
scores here are high, weather-station.md's chunk is a *plausible* top
match, just the wrong one.

## Checkpoint

- This course's premise, reproduced: a top-scoring chunk can be
  topically correct and factually wrong for the specific question asked,
  and naive top-`k` retrieval has no way to tell.
- A similarity threshold (`naive_rag` Lesson 14) doesn't help here,
  both chunks clear any reasonable threshold. The problem isn't "nothing
  scored high enough," it's "the wrong thing scored highest."
- This is the exact question this course keeps reusing through Lesson
  9, so grading, filtering, and correction all have one concrete failure
  to fix, rather than a new example every lesson.

If anything here still feels unclear, ask before moving to Lesson 3.
