# Lesson 4: Chunking a Document

## What we're building

A function that splits one text file into several smaller pieces,
called **chunks**. This is the first of Naive RAG's four stages, and the
only one that needs no AI call at all, it's plain text processing.

## Why chunk at all?

You could, in principle, embed an entire document as one giant vector
and skip chunking. Two problems make that a bad idea in practice: first,
embedding models have an input length limit, a large document may not
fit in one call at all. Second, and more importantly, a whole-document
embedding blurs together everything in that document into one average
"meaning," so a question about one specific detail (how the weather
station backs up its data, say) gets diluted by everything else in the
file (how it's built, how it fails) and becomes harder to match
precisely.

Chunking fixes both: each chunk is short enough to embed cleanly, and
each chunk's embedding represents one focused idea, so a question about
one topic (the pizza recipe, say) can match specifically against the
chunk that's actually about that topic, instead of an average of five
unrelated topics blended together.

## The code, piece by piece

```python
paths = sorted(NOTES_DIR.glob("*.md"))
blocks = []
for path in paths:
    _heading, body = path.read_text().split("\n\n", 1)
    blocks.append(" ".join(body.split()))
return "\n\n".join(blocks)
```

This course's `fixtures/notes/` folder has five short files, each about
a different topic (a weather station, a garden, a pizza recipe, a
bookshelf, cello practice). This lesson combines all five into one
document, the way several source files often get concatenated before
chunking in a real pipeline. For each file: `.split("\n\n", 1)` throws
away its `# Title` heading (Markdown structure is Lesson 11's subject,
not this one), and `" ".join(body.split())` collapses every run of
whitespace, including the newlines between that file's own paragraphs,
into single spaces, so each file becomes exactly one paragraph-sized
block. Joining those five blocks back together with a blank line
between them recreates the shape of a single hand-written notes file,
five topics, each separated by a blank line.

```python
raw_chunks = text.split("\n\n")
```

The combined document separates each topic with a blank line, that's
what `\n\n` (two newline characters in a row) represents in the raw
text. Splitting on it gives one chunk per topic.

```python
return [chunk.strip() for chunk in raw_chunks if chunk.strip()]
```

`.strip()` removes leading/trailing whitespace left over from the split
(each chunk otherwise starts right after a newline). The `if chunk.strip()`
filter drops any empty strings that show up if the file has extra blank
lines, particularly a common one at the very end of the file.

## A real chunking strategy is more careful than this

Splitting on blank lines only works because this specific document
happens to separate topics that way. A real document (a PDF report, a
web page, a long article) won't always cooperate with such a simple
rule, some paragraphs run long, some documents have no blank lines at
all. This lesson's simple version is deliberately naive, matching this
whole course; Lesson 10 and Lesson 11 come back to chunking with the two
questions that actually matter in practice: *how big should a chunk be*,
and *where should the boundaries fall*.

## Running it

```bash
uv run python lessons/naive_rag/01_beginner/04_chunking_a_document/lesson.py
```

## Expected output

```
Split into 5 chunks:

  Chunk 1 (394 characters): The bookshelf in the study is organized by color, not by author or gen...
  Chunk 2 (453 characters): Currently learning Bach's Cello Suite No. 1, focusing on the Prelude m...
  Chunk 3 (792 characters): The garden at the back of the house has three raised beds. The first b...
  Chunk 4 (681 characters): The best pizza dough recipe found so far uses 00 flour, a 48-hour cold...
  Chunk 5 (664 characters): Project Aurora is a personal weather station built from a Raspberry Pi...
```

Chunks come out in alphabetical order by filename (`bookshelf.md`,
`cello-practice.md`, `garden.md`, `pizza-dough.md`,
`weather-station.md`), since `sorted(NOTES_DIR.glob("*.md"))` sorts by
filename.

## Checkpoint

- **chunk**: one small, focused piece of a larger document, the unit
  Naive RAG actually embeds and retrieves, never the whole document at
  once.
- **why chunk**: keeps each embedding within input limits and focused on
  one idea, instead of an unfocused average of the whole document.
- This lesson's paragraph-based split is a naive strategy that happens
  to work on this one file; Lessons 10-11 cover strategies that hold up
  on documents that aren't this cooperative.

If anything here still feels unclear, ask before moving to Lesson 5.
