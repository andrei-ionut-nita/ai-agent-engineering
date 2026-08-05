# Lesson 28: Embeddings and a vector store, searching by meaning

## Where we left off

Lesson 27 loaded `notes.txt` and split it into six focused chunks. This
lesson makes those chunks **searchable**, not by exact keyword matching,
but by meaning.

## Embeddings: turning text into numbers that capture meaning

```python
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
```

An **embedding** is a long list of numbers (a "vector") that represents
a piece of text. The key property that makes this useful: texts with
*similar meaning* end up with *similar numbers*, positioned close
together in that number-space, even if they don't share a single exact
word.

"A dog ran in the park" and "A puppy played outside" would embed to
nearby vectors, despite having almost no words in common, because their
meanings are close. This is a genuinely different idea from anything
earlier in this course, everything before this compared or searched
text, this compares *meaning*.

## A vector store: a searchable collection of embedded chunks

```python
vector_store = InMemoryVectorStore(embeddings_model)
vector_store.add_documents(chunks)
```

A **vector store** holds a collection of chunks, each one embedded into
its vector form, and knows how to efficiently find the chunks whose
vectors are *closest* to a new query's vector. `InMemoryVectorStore`
keeps everything in your program's memory, no separate database needed,
which makes it perfect for learning and small projects, though a
production system with millions of documents would use a dedicated
vector database instead.

## Searching by meaning, not by words

```python
query = "What do I know about baking bread at home?"
results = vector_store.similarity_search(query, k=2)
```

Here's the part worth sitting with. The query asks about "baking bread,"
but nothing in `notes.txt` mentions bread at all, the closest matching
chunk is actually about pizza dough. A plain keyword search (like
searching a text file with Ctrl+F) would find nothing, "bread" doesn't
appear anywhere in the file.

But run this lesson, and the pizza dough chunk comes back as the top
match anyway, because baking pizza dough and baking bread are
*conceptually* close: both involve dough, yeast, fermentation, and oven
temperature. The embedding captured that closeness even though the
exact words don't overlap.

`k=2` asks for the two closest chunks, not just one, in case more than
one chunk is relevant to a question.

## Why this matters for RAG

This is the actual mechanism that makes RAG work: instead of stuffing an
entire document into the model's context every time (expensive, and
eventually impossible past the context window, recall Lesson 25), you
embed the question, find just the few chunks that are actually
*relevant* to it, and only send those specific chunks to the model.
Lesson 29 does exactly that, wrapping this search as a tool an agent can
use.

## Running it

```bash
uv run python lessons/langchain/03_advanced/28_rag_embeddings_and_vectorstore/lesson.py
```

## Checkpoint

- **embedding**: a vector of numbers representing a piece of text's
  meaning, positioned close to other texts with similar meaning.
- **vector store**: a searchable collection of embedded chunks, capable
  of finding the closest matches to a new query.
- **similarity search**: finds chunks by *meaning*, not exact word
  matching, the actual mechanism underneath RAG.

If anything here still feels unclear, ask before moving to Lesson 29.
