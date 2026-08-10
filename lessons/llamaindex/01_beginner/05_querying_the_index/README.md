# Lesson 5: Querying the index

## The last step of the core loop

Lesson 1 named it: `Document` -> `Node` -> `Index` -> `QueryEngine`.
Lesson 4 built the `Index` and ended on a cliffhanger: an `Index`
stores and embeds, but it has no `.query()` method, it can't answer
anything by itself. This lesson wraps that same index in a
`QueryEngine`, the piece that actually answers questions.

`index.as_query_engine()` is the one-line way to get one, and calling
`.query(question)` on it runs two steps behind the scenes:

1. **Retrieve**: embed the question, find the Nodes in the index whose
   vectors are most similar to it (Lesson 6 isolates this step alone).
2. **Synthesize**: hand those retrieved Nodes to `Settings.llm` and ask
   it to answer the question using only that text.

This is the RAG pattern in full, and it's the same two-step shape
`lessons/langchain`'s RAG lessons (27-29) built by hand with a
retriever and a chain. LlamaIndex just gives it one call.

## The Response object

`.query()` doesn't return a plain string, it returns a `Response`
object with two attributes worth knowing:

| | What it is |
|---|---|
| `.response` | The synthesized answer text, what you'd show a user |
| `.source_nodes` | The `NodeWithScore` objects actually handed to the LLM |

Each item in `.source_nodes` wraps a `Node` (same object from Lesson 2,
carrying `.metadata` like `file_name`) with a `.score`, how similar
that Node's embedding was to the question's embedding. Printing
`.source_nodes` is how you'd cite sources in a real app, or debug a
wrong answer by seeing exactly what text the LLM was actually shown.

## The code, piece by piece

```python
query_engine = index.as_query_engine()
```

Wraps the `VectorStoreIndex` from Lesson 4 in a `QueryEngine`. No
arguments needed for the default behavior, Lesson 7 shows the
`response_mode` argument that controls how synthesis works.

```python
response = query_engine.query(question)
```

Runs retrieve -> synthesize and returns a `Response`, not a string.

```python
print(f"A: {response.response}")
for node in response.source_nodes:
    source = Path(node.metadata["file_name"]).name
    print(f"    - {source} (score={node.score:.4f})")
```

Prints the answer, then walks `.source_nodes` to show which files fed
the answer and how confident the retrieval step was about each one.

## Running it

```bash
uv run python lessons/llamaindex/01_beginner/05_querying_the_index/lesson.py
```

## Expected output

Answer wording is non-deterministic (the LLM paraphrases the source
text), captured from a real run, your exact phrasing may vary. Scores
are also not perfectly reproducible between runs (embedding calls can
vary slightly), but should stay close to these values:

```
Index built from 3 documents.

Q: How many vacation days do new hires get to use in their first 90 days?
A: New hires cannot use more than 5 vacation days during their first 90 days of employment.

  Source nodes used:
    - vacation_policy.txt (score=0.6895)
    - remote_work_policy.txt (score=0.6181)

Q: What is the one-time home office equipment stipend, and how long do I have to submit receipts?
A: The one-time home office equipment stipend is 800 EUR (for a desk, chair, and monitor), and receipts must be submitted within the first 60 days of employment.

  Source nodes used:
    - remote_work_policy.txt (score=0.6120)
    - expense_policy.txt (score=0.6061)
```

Note the second question's top source is correctly
`remote_work_policy.txt` (where the stipend is described), with
`expense_policy.txt` pulled in second because it's topically similar
(also about reimbursement), even though the receipt-submission-window
detail actually lives in the remote work policy too. The LLM's answer
is still correct, it's just worth noticing that retrieval isn't always
a single obviously-right Node, this is `similarity_top_k`'s default of
2 at work, which Lesson 6 makes explicit.

## Checkpoint

- **`index.as_query_engine()`**: wraps an `Index` in a `QueryEngine`,
  the piece that can actually answer questions, an `Index` alone
  cannot.
- **`.query(question)`** runs retrieve (find similar Nodes) then
  synthesize (ask the LLM to answer from them), and returns a
  `Response`, not a plain string.
- **`.response`**: the synthesized answer text.
- **`.source_nodes`**: the `NodeWithScore` objects actually used,
  each carrying the source Node's `.metadata` and a similarity
  `.score`, useful for citations and debugging.

If anything here still feels unclear, ask before moving to Lesson 6.
