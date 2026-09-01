# Lesson 11: Structure-Aware Chunking

## Where we left off

Lesson 10 fixed a *word* getting cut in half by a chunk boundary.
There's a bigger version of the same problem: a chunk boundary can also
fall in the middle of two completely unrelated *topics*, mixing them
into one chunk that isn't really about either one. Overlap doesn't fix
this, more overlap just means more of both topics leak into each
other's chunks. The real fix is chunking on the document's own
structure instead of an arbitrary character count.

## The problem, made obvious

This lesson concatenates three fixture files (weather station,
bookshelf, cello practice) into one document, the way multiple files
often get combined before chunking. Fixed-size chunking, blind to
where one file's content ends and the next begins, produces chunks like
this:

```
'...its bearings need re-oiling every few months, or the readings\nstart drifting low.\n\n\n# Bookshelf Organization\n\nThe bookshelf in the study is organiz'
```

That single chunk is about a wind sensor's maintenance schedule *and*
how a bookshelf is organized, two unrelated ideas, embedded together as
one blurry average. A question about either topic now competes against
irrelevant noise from the other one baked into the same vector.

## The code, piece by piece

```python
for line in lines:
    if line.startswith("#") and current:
        chunks.append("\n".join(current).strip())
        current = []
    current.append(line)
```

Walk the document line by line. Every line starting with `#` (a Markdown
heading) means "a new section is starting here": save whatever's been
collected in `current` as a finished chunk, reset `current`, then start
collecting again, including the heading line itself.

```python
if current:
    chunks.append("\n".join(current).strip())
```

After the loop, whatever's left in `current` (the last section, which
never got saved because no heading came after it) gets added as the
final chunk.

The result: one chunk per heading, in this lesson's case one chunk per
source file, each one a complete, single-topic unit.

## Running it

```bash
uv run python lessons/naive_rag/02_intermediate/11_structure_aware_chunking/lesson.py
```

## Expected output

```
Fixed-size (150 chars, no regard for structure): 11 chunks
  ...
  Chunk 5: 'r: its bearings need re-oiling every few months, or the readings\nstart drifting low.\n\n\n# Bookshelf Organization\n\nThe bookshelf in the study is organiz'
  ...

Structure-aware (one chunk per heading): 3 chunks

  Chunk 1 (684 characters): # Project Aurora
  Chunk 2 (421 characters): # Bookshelf Organization
  Chunk 3 (476 characters): # Cello Practice Log
```

## When this doesn't work as cleanly

This lesson's documents are unusually cooperative: each one has exactly
one heading, so "one chunk per heading" happens to equal "one chunk per
file." A document with many headings and long sections underneath each
one needs a hybrid approach in practice, split on structure first, then
fall back to something like Lesson 10's fixed-size splitting *within*
an overly long section, rather than embedding one enormous chunk per
heading. This course keeps that combination out of scope to stay
focused, but it's the natural next question once these two techniques
are both in hand.

## Checkpoint

- **structure-aware chunking**: splitting on a document's own
  boundaries (headings, in this lesson) instead of an arbitrary
  character count.
- The problem it solves is different from Lesson 10's: that lesson
  fixed a cut *within* one idea, this one prevents *unrelated* ideas
  from being blended into a single chunk.
- Real systems typically combine both: split on structure first, then
  apply size-based splitting within any section still too long to embed
  as one chunk.

If anything here still feels unclear, ask before moving to Lesson 12.
