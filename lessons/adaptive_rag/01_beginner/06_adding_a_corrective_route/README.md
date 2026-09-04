# Lesson 6: Adding a Corrective Route

## Where we left off

Lesson 5 left `ambiguous` unhandled on purpose, `route()` raised for it.
This lesson adds the third strategy: retrieve, grade, and only retry
with a broader query when the grade says the first attempt fell short.
That's this course's small, hand-rolled stand-in for `corrective_rag`'s
real grade-and-retry pipeline.

## Why ambiguous questions need a different shape than multi-hop ones

Lesson 4's `multi_hop` route always retrieves across the whole corpus,
unconditionally, it doesn't need to check whether that's necessary
first, because a multi-hop question is one you can already tell needs
several documents combined. An `ambiguous` question is different: it
might genuinely need multiple documents (the wind-speed question below
does), or a single well-chosen document might actually cover it fine.
Always paying for a broad retrieval on every ambiguous question would
waste calls on the cases where narrow retrieval was already enough. So
this route tries narrow first, grades the result, and only broadens when
grading says the narrow attempt actually came up short.

## The code, piece by piece

```python
GRADE_PROMPT = """You are grading whether a retrieved passage, by \
itself, fully covers a question, or leaves out related information a \
complete answer would need. ... respond with exactly one word: \
"sufficient" or "insufficient"."""
```

This is `corrective_rag` Lesson 3's grading idea, adapted: instead of
grading plain relevance (does this passage relate to the question at
all), this grades *completeness* (does this one passage, alone, cover
the whole question). A passage about wind speed sensors is clearly
relevant to a wind-speed question, but it's still `insufficient` if the
question's full answer also needs the garden's drying-out detail from a
different file.

```python
def answer_ambiguous(query: str, store: list[dict]) -> str:
    first_pass = retrieve(query, store, k=1)
    grade = grade_chunk(query, first_pass[0]["text"])

    if grade == "sufficient":
        return generate_answer(query, first_pass)

    broadened = broaden_query(query)
    second_pass = retrieve(broadened, store, k=len(store))
    return generate_answer(query, second_pass)
```

Retrieve narrow (`k=1`) first. Grade that one chunk. If it's already
sufficient, answer from it and stop, no wasted broad retrieval. If it's
not, rewrite the query to be broader (`corrective_rag` Lesson 6's
rewrite idea, reused here) and retry with a wide retrieval across the
whole corpus, the same shape Lesson 4's `multi_hop` route uses, so an
ambiguous question that turns out to need several documents gets them.

## Not real corrective_rag

`corrective_rag`'s own Beginner tier grades every chunk in a top-k
individually, filters out the bad ones, and only rewrites when *all* of
them fail (Lessons 3 through 7 there, each one piece). This lesson's
version grades a single chunk and either keeps it or throws the whole
narrow attempt away, a smaller mechanism that demonstrates the same
grade-then-retry idea without reimplementing the real pipeline. This
course's Lesson 21 wires in `corrective_rag`'s actual, already-verified
implementation later.

## Running it

```bash
uv run python lessons/adaptive_rag/01_beginner/06_adding_a_corrective_route/lesson.py
```

## Expected output

```
Q: What oven setting does the pizza dough recipe use?
  label: simple_factual
  A: <the highest oven setting>

Q: What two hobbies happen in the same room as the weather station?
  label: multi_hop
  A: <names both cello practice and the bookshelf, in the study>

Q: How does wind speed affect things around the house?
  label: ambiguous
  A: <should mention both the wind sensor's bearings needing re-oiling
      AND the garden beds drying out faster above 20 km/h>
```

The third answer is the one to watch: it should combine both angles on
wind speed, the sensor's own maintenance problem from
`weather-station.md` and the garden's drying-out problem from
`garden.md`, which only happens if grading correctly caught that the
narrow first pass wasn't enough and triggered the broader retry.

## Checkpoint

- **grade-then-retry**: retrieve narrow first, grade whether it's
  actually sufficient, only pay for a broader retrieval when the grade
  says the narrow one fell short.
- Grading for *completeness* (does this one passage cover the whole
  question) is a different question than grading for *relevance* (does
  this passage relate to the question at all), both are useful, this
  lesson needed the former.
- Three routes now exist: `simple_factual`, `multi_hop`, `ambiguous`,
  the full label vocabulary this course's Beginner tier classifies into.

If anything here still feels unclear, ask before moving to Lesson 7.
