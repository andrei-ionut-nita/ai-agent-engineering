# Lesson 21: Bounding Correction Loops

## Where we left off

Lesson 16 named it as a failure mode: nothing in Lessons 6-7's rewrite
loop guarantees a rewrite eventually succeeds. Left unbounded, a
question the corpus genuinely can't answer (Lesson 6's France example)
would keep triggering rewrite after rewrite, burning API calls forever
on a question with no answer to find. This lesson adds the guard:
`MAX_REWRITE_ATTEMPTS`, after which the pipeline gives up honestly
instead of retrying indefinitely.

## The code, piece by piece

```python
MAX_REWRITE_ATTEMPTS = 2

for attempt in range(MAX_REWRITE_ATTEMPTS + 1):
    ...
    if attempt == MAX_REWRITE_ATTEMPTS:
        break
```

`+1` because attempt 0 is the original query, not a rewrite, `2` max
rewrites means 3 total tries: the original, plus two rewritten attempts.
The loop exits on the final attempt without trying yet another rewrite.

```python
attempts_note = "" if not previous_attempts[1:] else f" (previous rewrite also failed: {previous_attempts[-1]!r})"
current_query = call_model(REWRITE_PROMPT.format(question=query, previous_attempts=attempts_note)).strip()
```

Each rewrite is told about the previous failed attempt, so a second
rewrite doesn't just paraphrase the first rewrite's wording, it's
nudged toward trying a genuinely different angle instead of converging
on the same dead end twice.

```python
return (
    f"I don't have any information relevant to that question, after "
    f"{MAX_REWRITE_ATTEMPTS} rewrite attempt(s), nothing relevant was found."
)
```

The honest fallback, once the bound is hit, same spirit as every
earlier "I don't have any information relevant" message in this course,
just now explicit about *how hard* it tried before giving up.

## Running it

```bash
uv run python lessons/corrective_rag/03_advanced/21_bounding_correction_loops/lesson.py
```

## Expected output

```
Q: What is the capital of France?  (max 2 rewrite attempts)

  attempt 0: query='What is the capital of France?' -> 0 relevant chunk(s)
  attempt 1: query='<a rewritten variant>' -> 0 relevant chunk(s)
  attempt 2: query='<a different rewritten variant>' -> 0 relevant chunk(s)

Final answer: I don't have any information relevant to that question, after 2 rewrite attempt(s), nothing relevant was found.
```

Exactly 3 attempts run (1 original + 2 rewrites), then the loop stops,
regardless of how many more rewrites might theoretically be tried. The
exact rewritten wording varies each run.

## Checkpoint

- **Bounded correction**: a fixed maximum number of rewrite attempts,
  after which the pipeline reports failure honestly instead of retrying
  indefinitely against a corpus that was never going to answer.
- Telling each rewrite attempt about the previous one's failure reduces
  (doesn't eliminate) the risk of converging on the same unhelpful
  wording twice.
- This bound is what makes Lesson 22's real external-search branch safe
  to add next, a bounded internal loop that gives up cleanly is a
  reasonable trigger for falling back to an external source, an
  unbounded one would just add cost on top of cost.

If anything here still feels unclear, ask before moving to Lesson 22.
