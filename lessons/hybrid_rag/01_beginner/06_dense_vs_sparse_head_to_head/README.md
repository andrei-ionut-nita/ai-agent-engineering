# Lesson 6: Dense vs. Sparse, Head to Head

## Where we left off

Lessons 1-5 built both retrievers and showed each one struggle in
isolation. This lesson runs both, side by side, against the same ten
questions, five built around a bare exact token, five built as
paraphrases avoiding the answer's own technical vocabulary, and counts
hits and misses for each.

## The code, piece by piece

```python
LEXICAL_QUESTIONS = [
    ("20240115", "home_network.md"),
    ("E3D-CHT-04", "3d_printer.md"),
    ...
]
```

Each lexical question is just the bare ID, model number, or product
name, nothing else. No topic words to give dense retrieval anything to
lean on beyond the token itself, this is deliberately the hardest
version of the question, closer to someone pasting an error code into a
search box than asking a full sentence.

```python
SEMANTIC_QUESTIONS = [
    ("Why does my video call in the back bedroom keep freezing?", "home_network.md"),
    ...
]
```

Each semantic question paraphrases its answer, deliberately avoiding the
technical vocabulary (`"firmware"`, `"build"`) the actual document uses.
A couple of ordinary setting words (`"back bedroom"`) still leak through
by coincidence, Lesson 15 measures this precisely, but none of the words
doing the real explanatory work overlap, dense retrieval's home turf,
sparse retrieval has little beyond coincidence to match on.

## Why this happens, not just that it happens

An embedding model is trained to place text with similar *meaning*
close together. A token like `20240115` or `E3D-CHT-04` doesn't carry
much meaning on its own, so the model falls back on whatever meaning
*surrounds* it, the document's overall topic. That's normally a
reasonable fallback, until two documents share the same topic and only
the exact token distinguishes them (this course's `home_network.md` and
`old_travel_router.md`, both about router firmware). Then dense
retrieval genuinely can't tell them apart, because the one thing that
would tell them apart is the one thing it doesn't represent well.

BM25 has the opposite blind spot for the opposite reason: it only ever
sees literal token overlap. A paraphrase like `"video call keeps
freezing"` shares almost no *technical* vocabulary with a document that
explains the cause as a firmware bug dropping the 5GHz radio, so BM25
has little basis to connect the two, it isn't wrong so much as blind to
a signal (meaning, independent of exact wording) it was never built to
see.

## Running it

```bash
uv run python lessons/hybrid_rag/01_beginner/06_dense_vs_sparse_head_to_head/lesson.py
```

## Expected output

```
kind      dense  sparse  question
lexical   MISS   HIT     20240115
lexical   HIT    HIT     E3D-CHT-04
lexical   HIT    HIT     Puly Caff Plus
lexical   HIT    HIT     FoliGrow 9-3-6
lexical   HIT    HIT     8 Nm
semantic  HIT    HIT     Why does my video call in the back bedroom keep freezing?
semantic  HIT    MISS    Why do vertical walls have ridges even though I didn't change any settings?
semantic  HIT    HIT     Why is my espresso tasting sour and weak lately?
semantic  HIT    HIT     Why does my fig tree keep losing leaves from the bottom?
semantic  HIT    HIT     Why does my bike skip gears when climbing hills?

Dense overall:  9/10   (lexical: 4/5, semantic: 5/5)
Sparse overall: 9/10   (lexical: 5/5, semantic: 4/5)
```

Both retrievers land at 9/10 overall, an identical score hiding two
completely different failure shapes: dense's one miss is a bare ID with
a topically-confusable competitor in the corpus; sparse's one miss is a
paraphrase that avoids the answer's technical vocabulary entirely
(Lesson 15 measures exactly how much overlap remains, and it isn't
zero, just not the words that matter). Neither retriever is "better,"
they're wrong in different, close-to-opposite places, which is the
entire premise the rest of this course is built on.

## Checkpoint

- Dense and sparse retrieval fail on different question shapes, not
  randomly, on the *same corpus and the same overall accuracy*.
- Dense's blind spot: two documents sharing a topic, distinguished only
  by a token that carries little meaning on its own.
- Sparse's blind spot: a paraphrase with zero literal token overlap with
  its answer.
- Neither fix is "try harder," each retriever is doing exactly what it
  was built to do, which is why the fix is combining them, not picking a
  winner.

If anything here still feels unclear, ask before moving to Lesson 7.
