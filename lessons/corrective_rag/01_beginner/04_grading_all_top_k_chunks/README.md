# Lesson 4: Grading All Top-k Chunks

## Where we left off

Lesson 3 graded exactly one chunk, the top-1 result, and confirmed it
was wrong. But grading only the top result means the correct chunk
(`bookshelf.md`, ranked second by score) never even gets a chance,
grading can't rescue a chunk it never sees. This lesson over-fetches
before grading: retrieve `k=3` instead of `k=1`, then grade every one of
them.

## Why over-fetch first

This is the move that makes correction-by-filtering possible at all.
If retrieval only ever returns its single best guess, grading that one
chunk "not relevant" leaves you with nothing, no better off than before.
Fetching a few extra candidates up front, then grading all of them,
means a correct-but-not-top-ranked chunk (exactly `bookshelf.md`'s
situation here) is still in the pool when Lesson 5 filters by grade.

## The code, piece by piece

```python
K = 3
top_k = retrieve(QUESTION, store, K)
```

Same `retrieve()` as Lesson 2/3, just called with a larger `k`. Nothing
about retrieval itself changed, correction happens *after* this point,
not by making retrieval smarter.

```python
def grade_all(question: str, chunks: list[dict]) -> list[dict]:
    return [{**chunk, "grade": grade_chunk(question, chunk["text"])} for chunk in chunks]
```

Lesson 3's `grade_chunk()`, called once per retrieved chunk instead of
once. Each chunk keeps its score *and* gains a grade, both pieces of
information survive into Lesson 5.

## Running it

```bash
uv run python lessons/corrective_rag/01_beginner/04_grading_all_top_k_chunks/lesson.py
```

## Expected output

```
Q: Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?

Top-3 retrieved (before grading):
  weather-station.md (score=0.7xxx)
  bookshelf.md (score=0.7xxx)
  cello-practice.md (score=0.5xxx)

Top-3, graded:
  weather-station.md: not_relevant
  bookshelf.md: relevant
  cello-practice.md: not_relevant

1/3 chunks graded relevant. ...
```

The third-ranked chunk will vary slightly by run (it's well below the
top two either way), but the pattern that matters, the highest-scoring
chunk graded not-relevant while a lower-scoring chunk is graded
relevant, should hold consistently.

## Checkpoint

- Grading needs something to grade, retrieval has to over-fetch (`k`
  larger than what generation will actually use) so a correct chunk
  ranked below the top spot is still available to be graded and kept.
- Score and grade are now two separate pieces of metadata carried
  alongside each chunk, correction (starting Lesson 5) acts on the
  grade, not the score.

If anything here still feels unclear, ask before moving to Lesson 5.
