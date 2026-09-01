# Lesson 16: Failure Modes, by Hand

## Where we left off

Lessons 10-15 each fixed one specific problem: a word split by a chunk
boundary, unrelated topics blended into one chunk, an irrelevant top-k
result, a citation-free answer. This lesson deliberately triggers two
failures none of those fixes fully solve, so you've actually seen them
happen before this course moves on to Advanced techniques.

## Failure 1: a question needing two documents at once

*"Is the weather station's wind speed reading representative of
conditions in the garden?"* only has a real answer if you combine
`garden.md` (raised beds sit in a wind funnel, drying faster than the
station's average suggests) with `weather-station.md` (what the station
actually measures). With `k=1`, retrieval only returns `garden.md`, so
the model can only ever partially reconstruct the picture.

This is Naive RAG's most fundamental retrieval limitation: it treats
every question as "find the single best matching passage," with no
concept of "this question needs several passages combined." Increasing
`k` (as this lesson also shows) helps when the pieces exist as separate,
individually-retrievable chunks, but Naive RAG has no way to know a
question is multi-part in the first place, or to go looking for a second
piece once the first one is found. Later courses in this series (Graph
RAG, Agentic RAG) tackle this directly, one with explicit relationships
between pieces of information, the other by letting the system decide
to retrieve again.

## Failure 2: a fact split across a chunk boundary

Lesson 10 already showed fixed-size chunking with no overlap splitting
the word "readings" across two chunks. This lesson reuses that exact
setup and asks a question about the split fact directly, using only the
chunk that contains "re-oiling" (what a similarity search would likely
rank highest). The model gets the first half of the answer clearly, and
visibly struggles with the second half, the sentence is cut off mid-word
in the actual retrieved text.

## Running it

```bash
uv run python lessons/naive_rag/02_intermediate/16_failure_modes_by_hand/lesson.py
```

## Expected output

```
--- Failure 1: a question needing two documents at once ---

k=1, retrieved: ['garden.md']
Answer: <a confident-sounding answer, built from garden.md's own passing
mention of the weather station, without the station's own data>

k=2, retrieved: ['garden.md', 'weather-station.md']
Answer: <often a more cautious answer, correctly noting the context
still doesn't fully settle the question>

--- Failure 2: a fact split across a chunk boundary ---

Retrieved chunk: 't of the whole setup has been the wind speed\nsensor: its bearings need re-oiling every few months, or the read'
Answer: <correctly answers the re-oiling frequency, then visibly
struggles with "the read[ing]s start drifting low," the part of the
sentence that got cut off by the chunk boundary>
```

The exact wording varies between runs. What doesn't vary: `k=1` never
has access to both documents no matter how the question is phrased, and
the split-chunk answer never has access to the words simply missing from
its one retrieved chunk. Interestingly, `k=2` sometimes produces a
*more* hedged answer than `k=1`, seeing more context can make a model
more aware of what it still doesn't know, not just more capable of
answering. That's a useful reminder that "give it more context" isn't a
universal fix on its own.

## Checkpoint

- **multi-hop questions**: a question whose answer requires combining
  more than one chunk, something top-k similarity search has no
  built-in way to detect or plan for.
- Increasing `k` can help multi-hop questions when the needed pieces are
  each individually retrievable, but it's a blunt fix: it doesn't
  understand the question needs multiple parts, it just returns more of
  whatever is closest.
- A fact split by a chunk boundary (Lesson 10's problem) doesn't just
  hurt retrieval, it visibly degrades what generation can honestly say,
  even when the right chunk (mostly) gets retrieved.

If anything here still feels unclear, ask before moving to Lesson 17.
