# Lesson 27: Loading a document and splitting it into chunks

## Why this lesson exists, right here

The next two lessons build **RAG** (Retrieval-Augmented Generation):
letting an AI answer questions using your own documents, not just what
it learned during training. Before any of that can work, you need two
things ready: the text loaded into a usable form, and broken into
pieces small enough to search over individually. That's this entire
lesson, no model calls at all, purely setup.

## Loading: reading text, wrapping it as a `Document`

```python
text = NOTES_PATH.read_text()
return Document(page_content=text, metadata={"source": str(NOTES_PATH)})
```

A LangChain **document loader**, underneath all the fancier versions
that read PDFs, web pages, or databases, is fundamentally doing this one
simple thing: read some text, and wrap it in a `Document` object.
`Document` bundles the raw text (`page_content`) together with
`metadata`, information about *where it came from*. Here, that's just a
file path, but this matters more than it might seem: later, when an
answer is generated from retrieved text, the metadata is how you'd trace
that answer back to its original source.

## Splitting: breaking one document into several chunks

```python
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
chunks = splitter.split_documents([document])
```

`data/notes.txt` is one file with five unrelated topics (a weather
station project, a garden, a pizza recipe, a bookshelf, cello practice).
Searching over the *whole file at once* later, in Lesson 28, would be
far less precise than searching over five separate, focused chunks,
each about one topic. `chunk_size=300` caps each chunk at roughly 300
characters; `RecursiveCharacterTextSplitter` tries to break at natural
boundaries (paragraph breaks, then sentences, then words) rather than
cutting mid-word wherever the character count happens to land.

Run the lesson, and you'll notice most chunks line up neatly with the
original paragraphs, but not always: the garden paragraph got split
across two chunks (chunk 1 and chunk 2), because it was too long to fit
under the 300-character cap in one piece. Splitting is a *best effort*
to preserve meaning, not a guarantee every topic stays perfectly intact.

## `chunk_overlap`: a safety margin at the boundaries

```python
chunk_overlap=30
```

When a chunk does get cut mid-topic, `chunk_overlap` repeats the last
30 characters of one chunk at the start of the next one. This softens
the damage of an awkward cut, a sentence sliced in half at least has a
little of its preceding context carried into the next chunk, instead of
starting from nothing.

## Running it

```bash
uv run python lessons/langchain/03_advanced/27_document_loading_and_splitting/lesson.py
```

You should see the document load (1299 characters), then get split into
6 chunks, mostly matching the file's natural paragraphs, printed with
their character counts.

## Checkpoint

- **document loader**: reads text from somewhere and wraps it as a
  `Document`, bundling `page_content` with source `metadata`.
- **`Document`**: LangChain's basic unit for a piece of text plus where
  it came from.
- **text splitter**: breaks one long document into smaller chunks, small
  enough to search over individually.
- **`chunk_overlap`**: repeats a bit of text between adjacent chunks, so
  an awkward mid-topic cut doesn't lose all surrounding context.

If anything here still feels unclear, ask before moving to Lesson 28,
where these chunks get turned into something searchable.
