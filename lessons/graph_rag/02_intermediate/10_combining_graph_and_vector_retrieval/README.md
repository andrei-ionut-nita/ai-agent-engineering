# Lesson 10: Combining Graph Traversal With Vector Retrieval

## Where we left off

Every Beginner-tier lesson picked its starting entity by hand:
`START_ENTITY = "humidity sensor"`, typed directly into the script,
because the fixtures are small enough that a human can just read them
and know where to start. A real system doesn't get that shortcut, it
receives a question as plain text and has to figure out, on its own,
which graph node to start traversing from. This lesson fixes that,
using a tool this course's readers already know well: embeddings.

## Why embeddings are the right tool for this, specifically

You might assume finding a starting node just means checking whether
any graph node's name appears as a literal substring of the question.
That works embarrassingly rarely: this lesson's own example question
below says "the sensor," not "humidity sensor," a phrasing gap a
substring check can't bridge but an embedding comparison can, since
"the sensor" and "humidity sensor" land close together in meaning even
though they don't share the same characters. This is precisely
`naive_rag` Lesson 3's cosine-similarity idea, reused for an entirely
different job: instead of ranking *chunks* by similarity to a question,
this ranks *graph nodes* by similarity to a question, then hands the
single best match to Lesson 7's traversal as its starting point.

## The code, piece by piece

```python
node_names = list(graph.keys())
node_vectors = embed_texts(node_names)
query_vector = embed_texts([query])[0]

best_node = max(
    node_names,
    key=lambda name: cosine_similarity(query_vector, node_vectors[node_names.index(name)]),
)
```

Embed every node name once (a single batched call, the same batching
habit `naive_rag` Lesson 5 established), embed the question once, then
pick whichever node's embedding is closest to the question's. This
`best_node` becomes the traversal's starting point, no hand-typed
`START_ENTITY` constant needed anymore.

```python
facts = gather_facts(graph, best_node, max_hops=3)
answer = generate_answer(query, facts)
```

Past choosing the starting node, this is Lesson 7's traversal and
generation, unmodified, with one adjustment worth noticing: `max_hops`
goes up to 3 here, from Lesson 7's 2. A vector-picked node is a
*semantic* match to the question, not necessarily the single closest
node to the answer in the graph itself, running this lesson's own
example shows the closest embedding match is `"greenhouse"`, a real and
reasonable match, but one hop further from Mia and the multimeter than
Lesson 7's hand-picked `"humidity sensor"` was. Automating the starting
point trades a little precision in *where* you start for not needing a
human to pick it, and this lesson pays that cost back with one extra
hop. Lesson 14 makes that tradeoff, and its downside, explicit.

## Running it

```bash
uv run python lessons/graph_rag/02_intermediate/10_combining_graph_and_vector_retrieval/lesson.py
```

## Expected output

```
Question: Who recalibrated the sensor that Dev flagged as drifting in the greenhouse, and what tool did they use?

Best-matching starting node (by embedding similarity): 'greenhouse'

Answer:
Mia recalibrated the humidity sensor that Dev flagged. <possibly a brief, honest hedge on the exact tool, same pattern as Lessons 7-9>
```

## Checkpoint

- Finding a starting entity by embedding similarity, rather than by
  hand or by exact string match, is what makes Graph RAG usable on
  questions phrased in the user's own words instead of the graph's
  exact vocabulary.
- This reuses `naive_rag`'s cosine-similarity mechanics for a different
  target: ranking graph nodes by relevance to a query, instead of
  ranking chunks.
- Vector search and graph traversal aren't competitors in this
  architecture, vector search answers "where do I start," and traversal
  answers "what do I gather from there," each doing the part the other
  can't.

**Try this yourself:** print the top three closest nodes by similarity,
not just the single best one, for this lesson's question. Are any of
the runner-up nodes also reasonable starting points? What happens if
you traverse from the second-best node instead of the best one, does
the answer still come out roughly right?

If anything here still feels unclear, ask before moving to Lesson 11.
