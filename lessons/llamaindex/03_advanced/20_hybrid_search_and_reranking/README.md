# Lesson 20: Hybrid Search and Reranking

## Retrieval is a two-stage problem in production

So far, every query has trusted a single stage of retrieval: embed the
question, find the `similarity_top_k` nearest Nodes by vector distance,
hand them straight to the LLM. That works well at this course's tiny
fixture-data scale, but vector distance alone is an approximation, two
Nodes can sit close together in embedding space for surface reasons
(shared vocabulary, similar topic) without one of them actually being
the best answer to the question asked.

The common production fix is two stages: a cheap, broad first pass
(vector search, or hybrid search, more below) that overfetches a larger
candidate set, followed by a more expensive, more accurate second pass
that re-scores and trims that set down before it reaches the LLM. A
`node_postprocessor` is where that second stage plugs into LlamaIndex.

## LLMRerank: the reranker used here

`LLMRerank` is a `BaseNodePostprocessor` that asks the LLM itself to
directly judge each candidate Node's relevance to the query, rather than
trusting embedding distance. Passed via `node_postprocessors=[...]` on
`as_query_engine()`, it runs automatically after retrieval and before
response synthesis: the LLM that generates the final answer only ever
sees the reranked, trimmed set, `top_n` Nodes instead of the original
`similarity_top_k`.

This is the cheapest reranker to demo in this course because it needs
no extra model download, it's just another call to `Settings.llm`, the
same model already configured. A dedicated cross-encoder reranker (e.g.
`SentenceTransformerRerank`, in `llama_index.core.postprocessor.sbert_rerank`)
is often faster and cheaper per call in production, but requires
downloading a separate model, out of scope for a course that shares one
API key's quota across many concurrent lessons.

## Hybrid search, conceptually (not run here)

"Hybrid search" means combining two different retrieval signals, usually
dense vector similarity (what every lesson so far has used) plus sparse
keyword/BM25 search, then merging their rankings. The two catch
different failure modes: vector search is good at *semantic* matches
(different wording, same meaning) but can miss an exact rare term (a
product code, a specific policy name); keyword search is the opposite,
exact-match strong, semantically blind. Combining both is a common
production pattern for retrieval quality.

This isn't demoed as runnable code here because LlamaIndex's
in-memory `VectorStoreIndex` (the store used throughout this course, no
separate vector database process) doesn't expose a built-in hybrid
retriever the way a backend like Qdrant, Weaviate, or Pinecone does.
Wiring up genuine hybrid search would mean adding one of those external
vector store integrations, a fragile, heavyweight addition for a course
lesson. `LLMRerank`, demoed above, solves a related problem
(precision after retrieval) without that dependency.

## The code, piece by piece

```python
base_retriever = index.as_retriever(similarity_top_k=3)
base_nodes = base_retriever.retrieve(question)
```

Plain vector retrieval, no reranking, `similarity_top_k=3` returns the 3
nearest Nodes by embedding distance, with their raw similarity scores.

```python
reranker = LLMRerank(top_n=2)
query_engine = index.as_query_engine(
    similarity_top_k=3,
    node_postprocessors=[reranker],
)
```

`similarity_top_k=3` still runs the same broad first-pass retrieval.
`node_postprocessors=[reranker]` adds the second pass: `LLMRerank` asks
the LLM to score all 3 candidates, keeps only the `top_n=2` best-judged
ones. Note the two params answer different questions: `similarity_top_k`
controls the initial candidate pool size, `top_n` controls how many
survive reranking, `top_n` should always be `<= similarity_top_k`.

```python
response.source_nodes  # the reranked, trimmed nodes actually used
```

After a query through a query engine with a reranking postprocessor,
`source_nodes` reflects the post-reranking set (with new scores from
the reranker, not the original vector distances), not the raw retrieval
output.

## Running it

```bash
uv run python lessons/llamaindex/03_advanced/20_hybrid_search_and_reranking/lesson.py
```

## Expected output

Captured from a real run. Node ordering and exact scores can vary
slightly between runs (LLMRerank's judgment is itself an LLM call), and
in this particular run `LLMRerank` judged only one of the three candidates
relevant enough to keep, even though `top_n=2` allowed up to two, an
example of `top_n` being a ceiling, not a guarantee it always fills:

```
Q: How many vacation days do new hires get in their first 90 days?

Base retrieval (similarity_top_k=3, vector distance only):
  0. [vacation_policy.txt] score=0.6977  Nimbus Robotics: Vacation and Time Off Policy  Full-time employees at ...
  1. [remote_work_policy.txt] score=0.6230  Nimbus Robotics: Remote Work Policy  Nimbus Robotics operates on a hyb...
  2. [expense_policy.txt] score=0.5851  Nimbus Robotics: Expense Reimbursement Policy  Business expenses under...

After LLMRerank (top_n=2, LLM re-judges relevance):
  0. [vacation_policy.txt] score=10.0000  Nimbus Robotics: Vacation and Time Off Policy  Full-time employees at ...

Synthesized answer: New hires cannot use more than 5 days of vacation during their first 90 days of employment.
```

Note the reranker's score scale (0-10, an LLM-assigned relevance rating)
is not comparable to the base retriever's score scale (0-1, cosine
similarity), they're different measurements entirely, don't compare
them numerically across the two sections above.

## Checkpoint

- **Two-stage retrieval**: a broad, cheap first pass (vector similarity)
  followed by a narrower, more accurate second pass (reranking), a
  common production pattern once similarity search alone isn't precise
  enough.
- **`LLMRerank`**: a `node_postprocessor` that asks the LLM to directly
  re-judge each candidate Node's relevance, no extra model download
  needed since it reuses `Settings.llm`.
- **`node_postprocessors=[...]`** on `as_query_engine()` runs after
  retrieval, before synthesis; the LLM generating the final answer only
  sees the postprocessed Nodes.
- **Hybrid search** (vector + keyword/BM25) is a related but separate
  idea, combining two retrieval signals rather than re-scoring one; not
  demoed here since it needs an external vector store backend this
  course doesn't otherwise use.

If anything here still feels unclear, ask before moving to Lesson 21.
