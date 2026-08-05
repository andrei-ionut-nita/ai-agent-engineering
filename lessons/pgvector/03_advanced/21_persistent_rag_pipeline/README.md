# Lesson 21: A full RAG pipeline, backed by a store that survives a restart

## Where we left off

Lesson 20 swapped in `PGVector` but only proved retrieval. This lesson
builds the complete RAG chain, retrieve relevant chunks, stuff them
into a prompt, ask the model to answer *using only that context*, and
demonstrates the thing `InMemoryVectorStore` structurally cannot do:
run the program again, later, and the embeddings are already there.

## Checking before re-embedding

```python
def already_ingested(dsn: str, collection_name: str) -> bool:
    with psycopg.connect(dsn) as conn:
        row = conn.execute(
            """
            SELECT count(*) FROM langchain_pg_embedding e
            JOIN langchain_pg_collection c ON c.uuid = e.collection_id
            WHERE c.name = %s
            """,
            (collection_name,),
        ).fetchone()
        return row[0] > 0
```

`PGVector` stores its data in two tables it manages itself,
`langchain_pg_collection` (one row per named collection) and
`langchain_pg_embedding` (one row per embedded chunk, linked to its
collection). Checking this before calling `add_documents` again means a
second run of this script skips re-embedding entirely, no repeated API
calls, no duplicate rows, the whole point of a persistent store.

## The RAG chain itself

```python
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

prompt = ChatPromptTemplate.from_template(
    "Answer the question using only the context below.\n\n"
    "Context:\n{context}\n\nQuestion: {question}"
)

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
```

`as_retriever()` wraps any `VectorStore` (this one, or
`InMemoryVectorStore`, identically) as a `Runnable`, so it composes with
`|` exactly like every chain since langchain Lesson 6. `retriever |
format_docs` retrieves the top `k` chunks and joins them into one
string; `RunnablePassthrough()` passes the original question through
unchanged, both land in the prompt's `{context}` and `{question}`
slots. Everything past this point, the prompt, the model call, the
output parser, is unchanged from the LCEL patterns taught throughout
the langchain course.

## "Using only the context" is doing real work

Ask this chain about baking bread, notice the model correctly says it
doesn't know, because the retrieved context is about *pizza dough*, not
bread, rather than hallucinating an answer or blending in outside
knowledge. That instruction in the prompt is what keeps a RAG system
honest about the boundary between "what's in your documents" and "what
the model happens to already know."

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/03_advanced/21_persistent_rag_pipeline/lesson.py
```

Run it twice. The first run embeds and stores six chunks. The second
run prints "already ingested, skipping" and goes straight to answering,
proof the data survived between runs.

## Checkpoint

- `PGVector` stores data in `langchain_pg_collection` and
  `langchain_pg_embedding`, checkable directly to avoid redundant
  re-ingestion.
- **`as_retriever()`**: wraps any `VectorStore` as a composable
  `Runnable`, identical for `PGVector` and `InMemoryVectorStore`.
- A full RAG chain is just retrieval, formatting, a prompt, a model
  call, and a parser, composed with `|`, nothing new syntactically past
  what the langchain course already taught.

If anything here still feels unclear, ask before moving to Lesson 22.
