# Lesson 12: Multiple Documents and Metadata

## Where we left off

Lesson 9's checkpoint already loaded five separate files into one
vector store, but every record still only had `text` and `embedding`,
nothing said which file a chunk came from. That was fine for answering
questions, but it means you can't ever ask "search only within this one
document" or show a user "this answer came from `garden.md`." This
lesson adds exactly one new field, `source`, that fixes both.

## Metadata is just another field on the same dict

Nothing about the vector store's shape changes:

```python
{"text": text, "embedding": vector, "source": path.name}
```

It's the same `{text, embedding}` record from Lesson 5, with one more
key. **Metadata**, in RAG generally, just means "any field alongside a
chunk's text and embedding that isn't used for similarity search
directly, but is still useful": a source filename, a page number, a
timestamp, a category. Cosine similarity (Lesson 3) never looks at
`source`, it only ever compares `embedding` values; `source` is there
for filtering and for telling the user where an answer came from.

## The code, piece by piece

```python
def retrieve(query: str, store: list[dict], k: int, source: str | None = None) -> list[dict]:
    query_vector = embed_texts([query])[0]
    candidates = store if source is None else [r for r in store if r["source"] == source]
    ...
```

`source=None` (the default) searches the whole store, unchanged from
Lesson 6. Passing a specific filename first narrows `candidates` down to
just that one document's chunks, *before* scoring anything, then ranks
only within that narrower set. This is called **metadata filtering**:
using a non-embedding field to restrict what similarity search is even
allowed to consider.

## Running it

```bash
uv run python lessons/naive_rag/02_intermediate/12_multiple_documents_and_metadata/lesson.py
```

## Expected output

```
Indexed 5 documents: ['bookshelf.md', 'cello-practice.md', 'garden.md', 'pizza-dough.md', 'weather-station.md']

Plain search: weather-station.md (score=0.7xxx)
Scoped to cello-practice.md only: cello-practice.md (score=0.4xxx)
```

Notice the second result: forced to search only within
`cello-practice.md`, the function still returns *something*, its best
match within that one file, even though that file has nothing to do
with sensor maintenance. This is the same "top-k always returns
something" behavior from Lesson 8, now scoped: filtering narrows the
candidate pool, it doesn't guarantee any of the candidates are actually
relevant.

## Checkpoint

- **metadata**: any field on a chunk record besides its text and
  embedding, source filename, page number, category, anything useful
  for filtering or display but not for similarity itself.
- **metadata filtering**: narrowing the candidate pool by a non-embedding
  field before ranking by similarity, not instead of it.
- Filtering to the wrong document doesn't produce an error, it produces
  a confident but useless top match, worth remembering before trusting
  a scoped search's result.

If anything here still feels unclear, ask before moving to Lesson 13.
