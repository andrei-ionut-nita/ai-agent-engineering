# Lesson 5: Filtering Out Not-Relevant Chunks

## Where we left off

Lesson 4 graded three retrieved chunks and found exactly one relevant:
`bookshelf.md`, ranked *below* the top-scoring but wrongly-relevant
`weather-station.md`. This lesson does the obvious next thing with that
information: drop what's graded not-relevant, keep what isn't, and only
hand the survivors to generation. This is the first lesson where
correction actually changes the final answer, not just a printed grade.

## The code, piece by piece

```python
def filter_relevant(graded_chunks: list[dict]) -> list[dict]:
    return [chunk for chunk in graded_chunks if chunk["grade"] == "relevant"]
```

One line. Everything before this was setup, retrieval, grading, this is
the actual corrective act: a chunk's rank or score no longer matters
once it's graded not-relevant, it simply never reaches the prompt.

```python
print("Naive answer (top-1, no grading):")
print(f"  {generate_answer(QUESTION, top_k[:1])}\n")
...
print(f"Corrected answer (graded, filtered):")
print(f"  {generate_answer(QUESTION, filtered)}")
```

Both answers are generated and printed side by side specifically so you
can see the actual, textual difference correction makes, not just a
grade changing color in a printout. This is the answer-quality
comparison Lesson 17 will later turn into a repeatable score.

## Running it

```bash
uv run python lessons/corrective_rag/01_beginner/05_filtering_out_incorrect_chunks/lesson.py
```

## Expected output

```
Q: Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?

Naive answer (top-1, no grading):
  Based on the provided context, there is no mention of where the Raspberry Pi physically lives in the house.

Graded and filtered: 1/3 chunks kept
  kept: bookshelf.md
  dropped: weather-station.md
  dropped: cello-practice.md

Corrected answer (graded, filtered):
  Based on the provided context, Project Aurora's Raspberry Pi physically lives on a small shelf next to the bookshelf in the study...
```

The naive answer hedges (correctly refuses to guess, but that's still a
non-answer for a question the corpus can actually answer). The corrected
answer states the real location. That gap, hedge vs. a real grounded
answer, is what grading and filtering bought you.

## Checkpoint

- Filtering by grade, not by score, is the corrective act, everything
  in Lessons 1-4 was building the information this lesson finally acts
  on.
- This lesson's specific example resolves without ever needing a query
  rewrite (Lessons 6-7), because the correct chunk was already inside
  the over-fetched `k=3`, just outranked. Rewriting exists for a
  different situation: when *every* retrieved chunk grades not-relevant,
  which Lesson 6 demonstrates next.

If anything here still feels unclear, ask before moving to Lesson 6.
