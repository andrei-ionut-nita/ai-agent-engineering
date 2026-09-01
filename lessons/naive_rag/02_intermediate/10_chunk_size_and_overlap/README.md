# Lesson 10: Chunk Size and Overlap

## Where we left off

Lesson 4 split `notes.txt` on blank lines, a boundary that happened to
exist in that specific file. Most real documents don't hand you such a
convenient boundary, so this lesson introduces the more general
technique: **fixed-size chunking**, splitting text every `N` characters
regardless of where sentences or paragraphs fall, and the problem that
creates.

## The problem: a chunk boundary doesn't know what a sentence is

Cutting text every fixed number of characters will, sooner or later, cut
directly through the middle of a word or a sentence. When that happens,
the fact or detail that spanned the cut is now split across two chunks,
and neither chunk alone contains the complete idea. If retrieval only
returns one of those two chunks (which is likely, since half a fact is
also half as similar to a relevant question), part of the answer is
simply missing from what generation ever sees.

**Overlap** is the fix: instead of starting each new chunk exactly where
the last one ended, start it a little earlier, re-including the tail end
of the previous chunk. Whatever got cut off at the end of one chunk now
has a decent chance of appearing whole, at least once, somewhere.

## The code, piece by piece

```python
def fixed_size_chunks(text: str, size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return chunks
```

`start += size - overlap` is the whole idea in one line. With
`overlap=0`, each chunk starts exactly `size` characters after the last
one, no repetition, this is what Lesson 4's paragraph split effectively
did too, just at paragraph boundaries instead of a fixed character
count. With `overlap=30`, each new chunk starts 30 characters earlier
than that, so the last 30 characters of one chunk reappear as the first
30 characters of the next.

## Running it

```bash
uv run python lessons/naive_rag/02_intermediate/10_chunk_size_and_overlap/lesson.py
```

## Expected output

```
No overlap: 7 chunks of up to 110 characters
  ...
  Chunk 6: 't of the whole setup has been the wind speed\nsensor: its bearings need re-oiling every few months, or the read'
  Chunk 7: 'ings\nstart drifting low.\n'

With 30-character overlap: 9 chunks
  ...
  Chunk 8: 'hole setup has been the wind speed\nsensor: its bearings need re-oiling every few months, or the readings\nstart'
  Chunk 9: ' months, or the readings\nstart drifting low.\n'

--- The difference that matters ---

No-overlap chunk containing the whole word 'readings': None
With-overlap chunk containing the whole word 'readings': 'hole setup has been the wind speed\nsensor: its bearings need re-oiling every few months, or the readings\nstart'
```

Look closely at the no-overlap chunks 6 and 7: the word "readings" is
split across them as "...the read" and "ings...", so it doesn't appear
whole in *either* chunk, and neither does the complete idea ("the
readings start drifting low"). The overlapping version's Chunk 8
contains the whole sentence intact, because the extra 30 characters of
overlap happened to be enough to pull the cut point back before the
word started.

## Checkpoint

- **fixed-size chunking**: splitting text every `N` characters, simple
  and works on any document, but blind to sentence and word boundaries.
- **overlap**: re-including the tail of one chunk at the start of the
  next, so a fact that lands near a cut point still has a chance of
  appearing whole in at least one chunk.
- More overlap means more redundancy (the same text stored in multiple
  chunks) in exchange for fewer facts lost at a boundary, a real
  trade-off, not a free improvement, since more chunks means more
  embedding calls and a bigger vector store.

If anything here still feels unclear, ask before moving to Lesson 11.
