# Lesson 16: Failure Modes of Misrouting

## Where we left off

Every lesson so far assumed the classifier gets the label right. It
doesn't, always, and this lesson shows what happens on both sides of
that failure: a genuinely multi-hop question sent down the cheap naive
route, and a genuinely simple question sent down a more expensive route
than it needed.

## Failure 1: multi-hop, misclassified simple

*"What's kept in the same room as the weather station's Raspberry Pi?"*
needs `bookshelf.md` and `cello-practice.md` together, both
independently say they're in "the study," the same room the Pi lives
in per `weather-station.md`. Nothing about the question's phrasing
names two topics explicitly though, it reads like one factual lookup,
and this course's classifier (run for real, not staged) consistently
calls it `simple_factual`. Naive top-1 retrieval only ever returns
`bookshelf.md`, the single closest match, so the answer can only ever
name the bookshelf. Cello practice, the second thing that room
contains, is invisible to a route that only looked once.

This is the same fundamental gap `naive_rag` Lesson 16 demonstrated
with `k=1`: a route with no way to know a question needs more than one
document has no way to go looking for a second one. Here the failure
is one layer earlier, though: it isn't that `k=1` was too narrow for a
question correctly identified as needing more, it's that the
classifier itself never flagged the question as needing more in the
first place.

## Failure 2: simple, misclassified multi-hop

*"What wind speed dries out the garden beds faster?"* is fully
answerable from `garden.md` alone, the 20 km/h threshold sits in one
sentence there. That same sentence also mentions "the weather station's
average readings" in passing, enough shared vocabulary with
`weather-station.md` that the live classifier calls this question
`multi_hop` on some runs and `simple_factual` on others, the same
borderline instability Lesson 10 already measured (confidence around
0.85 on wind-speed questions, right at the edge). This lesson's code
pins the label to `multi_hop` for a repeatable demonstration, but it's
a real outcome this classifier actually produces, not a contrived one.

Unlike Failure 1, this isn't wrong: `garden.md` alone already answers
the question correctly, `weather-station.md` just rides along
unnecessarily. The cost isn't a bad answer, it's Lesson 14's cost, an
extra chunk and extra tokens spent on a question that never needed
them.

## Running it

```bash
uv run python lessons/adaptive_rag/02_intermediate/16_failure_modes_of_misrouting/lesson.py
```

## Expected output

```
--- Failure 1: a genuinely multi-hop question, misclassified simple ---

Q: What's kept in the same room as the weather station's Raspberry Pi?
  classifier label: simple_factual -> strategy: naive
  sources retrieved: ['bookshelf.md']
  answer: Based on the provided context, the bookshelf is kept in the same room as the weather station's Raspberry Pi [bookshelf.md].

The context does not mention what else, if anything, is kept in that room, so that information is missing.

--- Failure 2: a genuinely simple question, misclassified multi-hop ---

Q: What wind speed dries out the garden beds faster?
  label (forced, a real outcome on some runs): multi_hop -> strategy: multi_hop
  sources retrieved: ['garden.md', 'weather-station.md']
  answer: Based on the provided context, a stretch of days with a wind speed above 20 km/h dries out the raised beds noticeably faster than the weather station's average readings would suggest [garden.md].
```

Notice the model's own answer in Failure 1 is honest about what it's
missing, "the context does not mention what else... is kept in that
room", that's Lesson 15's grounded-answer instruction doing its job.
The honesty doesn't fix the failure, though: the missing information
about cello practice never had a chance to reach the model at all, no
amount of careful prompting recovers a document that was never
retrieved.

## Checkpoint

- **under-routing**: a multi-hop question sent down a route too narrow
  to see everything it needs, an incomplete answer with no error
  message, the model can only be honest about a gap it can't fill.
- **over-routing**: a simple question sent down a route wider (and more
  expensive) than it needed, not wrong, just wasteful, exactly the cost
  Lesson 14 measured.
- Both failures trace back to the same classifier, in a small enough
  question set that some questions genuinely sit right on the boundary
  between labels, where a small prompt difference can flip the outcome.
- A grounded, cite-your-sources answer (Lesson 15) can be honest about
  what's missing, but it can't retrieve what the router never asked
  for. Honesty about a gap and closing that gap are different problems.

If anything here still feels unclear, ask before moving to Lesson 17.
