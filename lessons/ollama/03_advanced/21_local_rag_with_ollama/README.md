# Lesson 21: Local RAG With Ollama

## Everything in this course, chained together

RAG (retrieval-augmented generation) is a pipeline, not a single call:
split a document into chunks, embed each chunk, embed a question, find
the chunks most similar in meaning to that question, then hand only
those chunks to a model as context for its answer. Every piece of that
pipeline has already appeared separately in this course:

- **Splitting**: `RecursiveCharacterTextSplitter`, the same tool
  langchain Lesson 27 uses, breaking `notes.txt` into topic-sized
  pieces.
- **Embedding**: `ollama.embed()`, from Lesson 8, turning chunks (and
  later, the question) into vectors.
- **Retrieval**: cosine similarity, also from Lesson 8, ranking chunks
  by how closely their meaning matches the question's.
- **Generation**: `ollama.chat()` with a system prompt telling the
  model to answer only from the given context, the same shape as
  Lesson 4.

This lesson is where those pieces become one working system, entirely
on your own machine, using the same source file (`notes.txt`) the
langchain course's document-loading lesson introduced.

## Why retrieval matters, not just "give the model everything"

```python
response = ollama.chat(
    ...,
    messages=[..., {"role": "user", "content": f"Context:\n{best_chunk}\n\nQuestion: {QUESTION}"}],
)
```

Only `best_chunk`, the single most relevant piece, goes into the
prompt, not the entire `notes.txt`. For a six-chunk file that
distinction barely matters, but the whole reason RAG exists is that
real knowledge bases are far too large to fit in any context window
(Lesson 19), and even when they'd technically fit, unrelated content
just adds noise a model has to sift through. Retrieval keeps what the
model actually sees small and relevant, on purpose.

## The code, piece by piece

```python
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
chunks = splitter.split_text(text)
```

Unchanged from langchain Lesson 27: break the document into overlapping
pieces small enough to embed and reason about individually.

```python
chunk_embeddings = ollama.embed(model="nomic-embed-text", input=chunks).embeddings
question_embedding = ollama.embed(model="nomic-embed-text", input=[QUESTION]).embeddings[0]
```

Two embedding calls, one batched over every chunk, one for the
question alone, both using the same embedding model from Lesson 8 so
the resulting vectors are directly comparable.

```python
ranked = sorted(
    zip(chunks, chunk_embeddings),
    key=lambda pair: cosine_similarity(question_embedding, pair[1]),
    reverse=True,
)
best_chunk = ranked[0][0]
```

The pgvector course does this ranking inside Postgres itself, with the
`<=>` operator and a real index, essential once you have thousands or
millions of chunks. Here, with six chunks, sorting a plain Python list
is honest about what's actually happening underneath any vector
database: the same cosine similarity math, just at a scale where an
index isn't needed yet.

## Running it

```bash
uv run python lessons/ollama/03_advanced/21_local_rag_with_ollama/lesson.py
```

## Expected output

```
Split notes.txt into 6 chunks.

Question: What instrument is being practiced?
Most relevant chunk:
Music practice log: currently learning Bach's Cello Suite No. 1 on the
cello, focusing on the Prelude movement. Practice sessions are thirty
minutes a day, five days a week, with a metronome set at a slow tempo
before gradually increasing speed.

Answer: The instrument being practiced is the cello.
```

The retrieved chunk should be deterministic (embeddings for the same
text don't change), the final answer's exact phrasing may vary
slightly but should always correctly say "cello."

## Checkpoint

- **The RAG pipeline**: split, embed, retrieve, generate, four steps
  you've already learned individually, chained together here.
- **Why retrieval, not "just give the model everything"**: keeps the
  model's real input small and relevant, essential once a knowledge
  base outgrows any context window.
- **Sorting in Python vs a real vector database**: the same cosine
  similarity math either way, a database (pgvector course) earns its
  place once chunk counts grow far past what fits comfortably in memory.

If anything here still feels unclear, ask before moving to Lesson 22.
