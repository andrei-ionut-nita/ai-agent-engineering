# Lesson 14: Limiting Traversal Depth

## Where we left off

Lesson 6 already showed, in passing, that two-hop traversal from
"multimeter" reaches the soldering station and the spare Raspberry Pi,
neither relevant to a humidity-sensor question. Lesson 10 needed three
hops instead of two just to compensate for a vector-picked starting
node landing one hop further out. This lesson stops treating hop depth
as an afterthought and tunes it properly: what's the smallest depth
that still answers this course's questions, and what breaks, precisely,
once depth goes higher than that.

## Why "more hops, to be safe" is the wrong instinct

Lesson 6 already named the mechanism: a graph node has some average
number of outgoing edges (call it its *branching factor*), and each
additional hop doesn't add that many new nodes, it *multiplies* the
reachable set by roughly that factor again. With this course's own
fixture graph averaging around four to five edges per node, hop 1
reaches roughly five nodes, hop 2 roughly twenty-five, hop 3 roughly a
hundred, well past this course's entire ~50-node graph by hop 3 or 4.
You might assume a bigger, deeper search is always more thorough, the
same way a bigger `k` felt safer in `naive_rag`. It isn't: past a
certain depth, *every* traversal reaches almost the entire graph
regardless of where it started, at which point depth has stopped doing
any useful filtering at all, and the "gathered facts" handed to
generation are barely different from just dumping the whole graph into
the prompt.

## What this lesson actually tunes against

This matters enough to state explicitly, per this course's shared
convention: the depth value chosen here is tuned by hand, against
direct observation of *this lesson's own traversal output* (does
depth 1 miss the answer, does depth 4 pull in Priya's book club for a
sensor question), not against Lesson 17's labeled precision@k question
set. That's the safe order: Lesson 17's score, reported later, is
evaluating a traversal depth that was picked *before* that score
existed, not fit to it after the fact. Tuning a hyperparameter against
the same set you later report a score on would be exactly the
train/test contamination `naive_rag` Lesson 17's "Why this doesn't
generalize (yet)" section warns about, this lesson deliberately avoids
that trap by choosing depth from a different signal entirely: a direct
before/after look at what each depth actually retrieves.

## The code, piece by piece

```python
for depth in (1, 2, 3, 4):
    facts = gather_facts(graph, start, max_hops=depth)
    relevant = sum(1 for f in facts if any(term in f for term in RELEVANT_TERMS))
    print(f"depth={depth}: {len(facts)} facts gathered, {relevant} plausibly relevant")
```

`RELEVANT_TERMS` is a small, hand-picked list of words this lesson's own
question actually cares about ("sensor", "Mia", "multimeter",
"greenhouse"), used only to *count*, roughly, how much of what got
gathered at each depth is on-topic versus noise. This is a rough
proxy, not a rigorous metric, its whole purpose is to make Lesson 6's
combinatorial-growth claim visible as a number you can watch climb
while relevance barely improves.

## Running it

```bash
uv run python lessons/graph_rag/02_intermediate/14_limiting_traversal_depth/lesson.py
```

## Expected output

```
depth=1: 6 facts gathered, 6 plausibly relevant
depth=2: 32 facts gathered, 23 plausibly relevant
depth=3: 63 facts gathered, 42 plausibly relevant
depth=4: 76 facts gathered, 46 plausibly relevant
```

Exact counts vary with extraction, the shape doesn't: total facts climb
steeply (roughly doubling each hop, as Lesson 6 predicted), while the
plausibly-relevant fraction of that total keeps shrinking (100% at
depth 1, down to roughly 60% by depth 4). The loose keyword match this
lesson uses for "relevant" is a rough proxy, not a precise one, so
don't expect a hard plateau, expect a shrinking share: past depth 2 or
3, an ever-larger slice of what got gathered is unrelated context that
generation has to wade through (or worse, gets subtly distracted by) to
find the two or three facts that actually answer the question.

## Checkpoint

- Traversal depth trades recall for precision combinatorially, not
  linearly, unlike `naive_rag`'s `k`, which trades them off roughly
  one-for-one.
- The right depth is usually small (2, sometimes 3), found by directly
  observing what each depth actually retrieves for real questions.
- This lesson's depth choice is tuned against direct observation of
  traversal output, a signal separate from Lesson 17's labeled
  precision@k set, exactly the safe ordering `naive_rag` Lesson 17
  describes and this course's own Lesson 17 will confirm.

**Try this yourself:** add `"greenhouse"` and `"Priya"` to
`RELEVANT_TERMS` is wrong on purpose, don't. Instead, print depth 4's
actual gathered facts (not just the counts) and scan for the first one
that's clearly off-topic for a humidity-sensor question, something from
`book-club.md`, say. If your extraction run doesn't reach that far in 4
hops, try 5 or 6. How many hops away from "humidity sensor" was the
first clearly-irrelevant fact, and does that match what Lesson 6
predicted about combinatorial growth?

If anything here still feels unclear, ask before moving to Lesson 15.
