# Lesson 2: Dense Retrieval, Recapped

## Where we left off

This course assumes you've either done [`naive_rag`](../../../naive_rag/)
or otherwise know what dense retrieval is: embed the query, embed every
chunk, rank by cosine similarity, take the top `k`. If either of those
last two sentences was new information, do `naive_rag`'s Beginner tier
first, this lesson compresses nine of its lessons into one script and
moves fast.

Lesson 1 showed dense retrieval's blind spot on an ID-heavy question.
This lesson shows the opposite: a question dense retrieval is *built*
for, so the rest of the course has a clear baseline for "when dense
alone is enough" before Lesson 3 starts building the thing that covers
what it isn't enough for.

## The code, piece by piece

```python
QUESTION = "Why does my espresso taste weak and sour lately?"
```

Notice what's missing: no "descale," no "Puly Caff," no "boiler," none
of the words the actual document uses. This is a paraphrase, in meaning
only, exactly the shape of question dense retrieval handles well.

```python
def build_store() -> list[dict]: ...
def retrieve(query_vector, store, k=2) -> list[dict]: ...
def generate(question, chunks) -> str: ...
```

The same three functions from `naive_rag` Lessons 5-7, unchanged: embed
and store, rank and take top-`k`, stuff into a prompt. This course
builds a second, independent retriever alongside this one starting
Lesson 3, then spends the rest of Beginner and Intermediate combining
the two, this function shape is the "dense half" of that combination.

## Running it

```bash
uv run python lessons/hybrid_rag/01_beginner/02_dense_retrieval_recap/lesson.py
```

## Expected output

```
Question: Why does my espresso taste weak and sour lately?

Dense retrieval top-2:
  0.7098  espresso_machine.md
  0.5280  3d_printer.md

Answer:
Based on the provided context, espresso tastes sour and thin due to old, stale scale buildup inside the boiler [espresso_machine.md].
```

Compare that top score (0.71) and margin (0.18) against Lesson 1's ID
question (0.65, margin 0.13). Same retrieval mechanism, same corpus,
meaningfully more confident and more correct on a question built around
meaning instead of an exact token.

## Checkpoint

- Dense retrieval: embed, rank by cosine similarity, take top `k` -
  unchanged from `naive_rag`, this course's "dense half."
- Paraphrased, meaning-based questions are dense retrieval's strength,
  confirmed by comparing this lesson's margin against Lesson 1's.
- Starting Lesson 3, a second retriever gets built from scratch to cover
  the gap Lesson 1 demonstrated, then the two get fused.

If anything here still feels unclear, ask before moving to Lesson 3.
