# Lesson 6: Retrievers, isolating retrieve from synthesize

## Splitting the pipeline in half

Lesson 5's `query_engine.query()` did two things in one call: retrieve
the most relevant Nodes, then ask the LLM to synthesize an answer from
them. This lesson isolates the first half. `index.as_retriever()`
returns a `Retriever`, an object whose only job is finding relevant
Nodes, no LLM call involved at all, just the one embedding call needed
to turn the question itself into a vector.

This matters for two practical reasons:

- **Debugging is cheaper and clearer.** If a `QueryEngine` gives a bad
  answer, the first question is always "did it retrieve the right
  Nodes?" Calling a retriever directly answers that without spending
  an LLM call, and without the LLM's synthesized wording obscuring
  what was actually found.
- **Retrieval is a separate concern from synthesis.** You can tune how
  Nodes are found (how many, what filters, what strategy) independently
  of how an answer gets written from them. A `QueryEngine` is really
  just a `Retriever` plus a response synthesizer wired together.

## `similarity_top_k`

`as_retriever(similarity_top_k=2)` controls how many Nodes come back,
ranked by how similar their embedding is to the question's embedding.
This is the same knob a `QueryEngine` uses internally (Lesson 5's
`.as_query_engine()` used the library default, 2, unstated), made
explicit here. A larger `similarity_top_k` retrieves more context at
the cost of a longer, more expensive synthesis step later, this is
exactly the setting that makes Lesson 7's `response_mode` differences
start to matter on real datasets.

## `.retrieve()` returns raw evidence

```python
results = retriever.retrieve(question)
```

Returns a plain list of `NodeWithScore` objects, the same type found
inside `response.source_nodes` in Lesson 5, but this time it's the
whole result, not a side channel next to a synthesized answer. Each
one carries the Node's full `.text`, its `.metadata` (source file), and
a `.score`.

## The code, piece by piece

```python
retriever = index.as_retriever(similarity_top_k=2)
results = retriever.retrieve(question)
```

Builds a retriever from the same `VectorStoreIndex` Lesson 4 built, and
retrieves the top 2 most similar Nodes to `question`. No `Settings.llm`
call happens anywhere in this line.

```python
for i, node in enumerate(results):
    source = Path(node.metadata["file_name"]).name
    print(f"--- Result {i} (from {source}, score={node.score:.4f}) ---")
    print(node.text.strip())
```

Prints each retrieved Node's full text alongside its source file and
score, exactly what a `QueryEngine` would have handed to the LLM to
synthesize from, visible here directly instead of buried inside
`response.source_nodes`.

## Running it

```bash
uv run python lessons/llamaindex/01_beginner/06_retrievers/lesson.py
```

## Expected output

No LLM call is made in this lesson, so node text is exact; scores can
vary slightly between runs but should stay close to these values:

```
Index built from 3 documents.

Q: What is the core collaboration hours window for remote employees?

Retrieved 2 nodes (no LLM call made):

--- Result 0 (from remote_work_policy.txt, score=0.6640) ---
Nimbus Robotics: Remote Work Policy
...
Core collaboration hours, when every team member is expected to be
reachable regardless of which days they're in the office, are 11:00 to
16:00 Cluj time.

--- Result 1 (from vacation_policy.txt, score=0.6036) ---
Nimbus Robotics: Vacation and Time Off Policy
...

as_retriever() = retrieval only, no LLM call.
as_query_engine() = retrieval + synthesis (Lesson 5), one extra LLM call.
```

(Full Node text for both results is printed when you actually run it,
trimmed here for length.) Notice the second result, the vacation
policy, isn't actually about collaboration hours; with only 3 Nodes
total in this tiny index, `similarity_top_k=2` is retrieving more than
half of everything that exists, so a topically-unrelated Node with a
lower score still makes the cut. This is normal and harmless here
(Lesson 5 showed the LLM still gave a correct, focused answer using
only the relevant Node), but it's exactly the kind of thing worth
checking retrieval output for on a real, larger dataset.

## Checkpoint

- **`index.as_retriever(similarity_top_k=k)`**: builds a `Retriever`,
  retrieval only, no LLM call, no synthesized answer.
- **`.retrieve(question)`**: returns a list of `NodeWithScore` objects
  ranked by similarity, the raw evidence a `QueryEngine` would
  otherwise hand straight to the LLM.
- **`similarity_top_k`**: how many Nodes come back; a `QueryEngine`
  uses this same setting internally, just with a default value if you
  don't set it yourself.
- **Retrieve vs query**: a `Retriever` finds relevant Nodes; a
  `QueryEngine` (Lesson 5) is a `Retriever` plus a synthesis step that
  turns those Nodes into a written answer.

If anything here still feels unclear, ask before moving to Lesson 7.
