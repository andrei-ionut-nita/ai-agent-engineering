# Lesson 15: Prompting for Disclosed Corrections

## Where we left off

Every corrective lesson so far printed what happened (grades, dropped
chunks, rewrites) to the terminal, for you, the developer. A real user
never sees that, they see the final answer. This lesson makes the
correction visible in the answer itself: if a retrieved passage was
dropped as not relevant, the generated answer says so.

## Why disclosure matters here specifically

`naive_rag` Lesson 15 taught citations and "I don't know" as trust
signals. Corrective RAG has a third one this course adds: telling the
user retrieval initially reached for the wrong thing and was corrected.
That's useful information, a user who sees "a passage about the weather
station itself was dropped as not relevant" understands *why* the
system didn't just answer from the first thing it found, which is more
trustworthy than a clean answer that silently hides a near-miss.

## The code, piece by piece

```python
dropped_sources = ", ".join(c["source"] for c in dropped)
if dropped:
    correction_note = (
        f"Before generating this answer, {len(dropped)} retrieved "
        f"passage(s) that scored high on similarity were graded not "
        f"relevant and dropped, specifically: {dropped_sources}. You "
        "MUST end your answer with one short new sentence starting "
        f"exactly with 'Correction:' explaining that {dropped_sources} "
        "was retrieved but dropped as not relevant to this specific "
        "question."
    )
```

A soft instruction ("mention it if you'd like") didn't reliably produce
a disclosure in testing, models tend to just answer the question and
skip optional asides. A specific, mandatory instruction (a fixed
sentence prefix, told exactly which source to name) is what actually
made disclosure show up consistently. This is the same lesson `naive_rag`
Lesson 15's citation formatting already taught: vague prompt
instructions produce inconsistent output, specific ones don't.

```python
    correction_note = "No passages were dropped, nothing to disclose."
```

When nothing was dropped, the instruction says so plainly, so the model
isn't tempted to invent a correction that didn't happen.

## Running it

```bash
uv run python lessons/corrective_rag/02_intermediate/15_prompting_for_disclosed_corrections/lesson.py
```

## Expected output

```
Q: Project Aurora's Raspberry Pi writes sensor readings to a SQLite file on its SD card. Where does that Raspberry Pi physically live in the house?

  weather-station.md: not_relevant
  bookshelf.md: relevant
  cello-practice.md: <relevant or not_relevant, varies by run>

A: <an answer about the study/bookshelf shelf, citing [bookshelf.md]>

Correction: weather-station.md was retrieved but dropped as not relevant to this specific question.
```

The exact wording of the answer varies each run (and `cello-practice.md`'s
grade can go either way, both notes mention the same room), but the
final `Correction:` line should appear consistently whenever
`weather-station.md` was dropped, which this question reliably triggers.

## Checkpoint

- Disclosure needs a specific, mandatory prompt instruction, not a
  polite suggestion, to show up reliably in the model's output.
- Telling a user a correction happened, and which source was dropped
  and why, is a trust signal specific to Corrective RAG, on top of the
  citation and "I don't know" signals `naive_rag` already taught.
- Lesson 18's checkpoint reuses this exact idea as a visible "retrieval
  was corrected" indicator in a small search assistant.

If anything here still feels unclear, ask before moving to Lesson 16.
