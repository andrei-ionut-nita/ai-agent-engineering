# Lesson 4: Your first VectorStoreIndex

## The "index" step

Lesson 1 named the core loop: `Document` -> `Node` -> `Index` ->
`QueryEngine`. Lesson 2 built `Document`s and `Node`s by hand. Lesson 3
connected Gemini as both the LLM and the embedding model behind
`Settings`. This lesson puts them together and takes the third step:
building a real `Index`.

`VectorStoreIndex` is LlamaIndex's most common index type, and its
`from_documents()` classmethod is the one-line version of the whole
pipeline you saw broken apart in Lesson 2:

1. Split every `Document` into `Node`s, using `Settings`' default node
   parser (a `SentenceSplitter`) unless you configure a different one.
2. Call `Settings.embed_model` on every `Node`'s text, turning each one
   into a vector.
3. Store the `Node`s and their vectors together in a vector store,
   ready for similarity search.

This is the LlamaIndex equivalent of LangChain's
`Chroma.from_documents(docs, embedding=...)`, except the vector store
here is a plain in-memory one by default, no separate database process
needed for a course-sized set of documents.

## Building an index costs API calls

Step 2 above makes one embedding API call per `Node`, so
`VectorStoreIndex.from_documents()` is not free or instant the way
splitting text into `Node`s was in Lesson 2. For this course's tiny
fixture files that's three calls, but it's worth internalizing now:
indexing cost scales with the number of `Node`s, not the number of
`Document`s. This is also why Lesson 21 (persisting and loading
indexes) matters as soon as your data stops being three small `.txt`
files, you don't want to re-embed the same documents on every run.

## An Index alone doesn't answer questions

`VectorStoreIndex` is a storage and retrieval structure, not something
you can ask a question directly. It has no `.query()` method. Lesson 5
wraps this same index in a `QueryEngine`, the piece that actually
retrieves relevant `Node`s for a question and asks the LLM to
synthesize an answer from them.

## The code, piece by piece

```python
index = VectorStoreIndex.from_documents(documents)
```

Runs all three steps above in one call, reading `Settings.llm` and
`Settings.embed_model` implicitly (Lesson 3's global pattern), no model
objects passed in explicitly.

```python
print(f"Index built. Nodes stored: {len(index.docstore.docs)}")
```

`index.docstore` is the index's internal store of every `Node` it
holds, keyed by `node_id`. Its length is the node count, here 3, one
per fixture file, because each policy file is short enough to fit in a
single `SentenceSplitter` chunk at the default settings.

```python
first_node_id = next(iter(index.docstore.docs))
first_node = index.docstore.docs[first_node_id]
```

`index.docstore.docs` is a dict of `node_id -> Node`. Grabbing the
first key and looking it up is a way to peek at one stored `Node`
directly, same shape of object Lesson 2 built by hand with
`SentenceSplitter`, just now living inside the index alongside its
embedding vector.

## Running it

```bash
uv run python lessons/llamaindex/01_beginner/04_first_vector_index/lesson.py
```

## Expected output

The node text preview is stable (no LLM wording involved, only
embedding calls), captured from a real run:

```
Loaded 3 documents

Index built. Nodes stored: 3

First stored node:
  source file: expense_policy.txt
  text preview: Nimbus Robotics: Expense Reimbursement Policy

Business expenses under 100 EUR c...

An Index stores and embeds; it doesn't answer questions on its own.
Lesson 5 wraps this index in a QueryEngine to actually query it.
```

## Checkpoint

- **`VectorStoreIndex.from_documents()`**: splits Documents into Nodes,
  embeds every Node, and stores Nodes + vectors together, one line
  doing the work Lesson 2 did by hand.
- Building an index makes one embedding API call per `Node`, cost
  scales with node count, not document count.
- `index.docstore.docs` is a dict of `node_id -> Node`, a way to
  inspect what's actually stored.
- An `Index` stores and retrieves; it does not answer questions by
  itself. `QueryEngine` (Lesson 5) is the layer that does.

If anything here still feels unclear, ask before moving to Lesson 5.
