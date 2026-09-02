# Lesson 3: Grading a Single Retrieved Chunk

## Where we left off

Lesson 2 proved the failure: naive top-1 retrieval returned
`weather-station.md`, a chunk that scored highest but doesn't answer the
question. This lesson adds the first piece of the fix, a **retrieval
evaluator**: a second Gemini call whose only job is judging whether a
retrieved chunk actually helps answer the question, independent of its
similarity score.

## Binary grading, not the full three-way grade yet

Yan et al. 2024's retrieval evaluator grades each chunk into three
confidence buckets: correct, ambiguous, incorrect. This lesson starts
simpler, on purpose, a binary relevant / not-relevant call. The paper's
"ambiguous" bucket exists to trigger *strip-level refinement* (keeping
only the useful sentences out of a partially-relevant chunk), and that
machinery doesn't exist yet, it arrives in Lessons 10-11. Grading
three ways before there's anything useful to do with the middle bucket
would just be extra complexity with no payoff. Lesson 12 upgrades this
exact function to the real three-way grade once strip-level refinement
gives "ambiguous" somewhere to go.

## The code, piece by piece

```python
GRADE_PROMPT = """You are grading whether a retrieved passage is relevant \
enough to help answer a question. Read the question and the passage, \
then respond with exactly one word: "relevant" or "not_relevant".
...
```

A constrained prompt: one question, one passage, one word out. Keeping
the grader's output this narrow (versus asking for a paragraph of
reasoning) makes it cheap to call per chunk (Lesson 19 puts a number on
this) and trivial to parse.

```python
def grade_chunk(question: str, chunk_text: str) -> str:
    ...
    grade = (response.text or "").strip().lower()
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"
```

Gemini reliably answers with just the word asked for, but this defends
against the occasional wrapped or slightly-off response rather than
crashing on it, `not_relevant` is checked first because the substring
`"relevant"` also appears inside `"not_relevant"`.

## Running it

```bash
uv run python lessons/corrective_rag/01_beginner/03_grading_a_retrieved_chunk/lesson.py
```

## Expected output

```
Q: Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?

Top-1 retrieved chunk: weather-station.md (score=0.7xxx)

Grade: not_relevant
```

The score is unchanged from Lesson 2, still the highest in the store.
The grade is new information the score alone couldn't provide.

## Checkpoint

- **retrieval evaluator**: a model call whose only job is judging
  whether a retrieved chunk actually answers the question, separate from
  and in addition to its similarity score.
- **Binary grading, deferred three-way grading**: this lesson's
  relevant/not-relevant call is a deliberate simplification of the
  paper's correct/ambiguous/incorrect grade, upgraded in Lesson 12.
- A high similarity score and a "not relevant" grade are not
  contradictory, they measure different things: one measures topical
  closeness, the other measures whether this specific passage answers
  this specific question.

If anything here still feels unclear, ask before moving to Lesson 4.
