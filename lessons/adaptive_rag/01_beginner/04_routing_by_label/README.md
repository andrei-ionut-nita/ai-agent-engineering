# Lesson 4: Routing by Label

## Where we left off

Lesson 3 built `classify()`, one function that turns a question into a
label. That label doesn't do anything yet, it's just printed. This
lesson gives it a job: given a label, dispatch the question to the
retrieval strategy suited to it. Two labels get real routes this lesson,
`simple_factual` and `multi_hop`; `ambiguous` still raises, that's
Lesson 6's job once corrective grading exists.

## Two routes, two very different retrieval shapes

`simple_factual` reuses `naive_rag`'s own shape exactly: retrieve the
single best-matching chunk, generate from it. One document is enough,
so `k=1` is the right amount to retrieve, not too little, not more than
necessary.

`multi_hop` needs something naive top-1 retrieval structurally can't
give it, more than one document reaching generation at once. This
lesson's `answer_multi_hop()` is a small, honest stand-in: retrieve
across every document in the store (this course's fixture set is five
short files, so "every document" is still cheap), and let Gemini
synthesize the answer out of whichever chunks are actually relevant.
This is **not** real graph traversal, there's no entity extraction, no
relationship edges, no hopping node to node the way `graph_rag`'s own
Beginner tier builds by hand. It's a lightweight placeholder for "make
sure no single top-k cutoff can accidentally leave out the one document
that carries half the answer." This course's Lesson 21 wires in
`graph_rag`'s real, already-built traversal implementation later; this
lesson intentionally does not reimplement it.

## Why k=3 wasn't enough, and k=all was

An earlier version of this lesson tried `k=3` for the multi-hop route.
Against the question "What two hobbies happen in the same room as the
weather station?", the top-3 by cosine similarity turned out to be
`bookshelf.md`, `weather-station.md`, and `garden.md`, missing
`cello-practice.md` entirely, the one file naming the second hobby. Wind
speed and gardening details scored closer to this question than cello
practice did, purely by embedding geometry, nothing about relevance.
That's precisely the kind of top-k miss real graph traversal exists to
avoid by following an explicit relationship instead of a similarity
score. This lesson's fix, retrieving across the whole (small) corpus
instead of guessing a k, is a reasonable stand-in at five documents, and
a preview of exactly why it stops being reasonable at scale, which is
what makes real multi-hop retrieval worth building properly later in
this series.

## The code, piece by piece

```python
def route(question: str, label: str, store: list[dict]) -> str:
    if label == "simple_factual":
        return answer_simple(question, store)
    if label == "multi_hop":
        return answer_multi_hop(question, store)
    raise ValueError(f"No route for label {label!r} yet, that's Lesson 6")
```

The whole routing decision, in one function: given a label already
produced by `classify()`, call the one strategy function that matches
it. Nothing fancier than an `if` chain, that's deliberate, Lesson 5
cleans this exact shape up into a reusable pattern, it doesn't need to
be more than this yet.

## Running it

```bash
uv run python lessons/adaptive_rag/01_beginner/04_routing_by_label/lesson.py
```

## Expected output

```
Q: What oven setting does the pizza dough recipe use?
  label: simple_factual
  A: <the highest oven setting, with a preheated steel>

Q: What two hobbies happen in the same room as the weather station?
  label: multi_hop
  A: <names both organizing the bookshelf and cello practice, in the study>
```

Unlike Lesson 1's k=1 failure, this lesson's second answer should
correctly name both hobbies, because the label routed it to a strategy
that actually retrieves both files.

## Checkpoint

- **routing**: dispatch on a label, call the strategy function that
  matches it, nothing more exotic than a conditional.
- `simple_factual` -> naive top-1, the right amount of retrieval for a
  single-document answer.
- `multi_hop` -> a hand-rolled, retrieve-broadly-and-synthesize stand-in,
  not real graph traversal, but enough to fix the specific failure
  Lesson 1 demonstrated.
- Widening `k` is a blunt fix that works at five documents and stops
  scaling well; real multi-hop retrieval (`graph_rag`'s traversal) is
  what this series built to replace it properly.

If anything here still feels unclear, ask before moving to Lesson 5.
