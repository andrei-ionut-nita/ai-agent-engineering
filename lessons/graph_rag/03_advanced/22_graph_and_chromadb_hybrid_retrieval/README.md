# Lesson 22: Graph + `chromadb` Hybrid Retrieval

## Where we left off

Lesson 10 found a traversal's starting node by embedding every node
name and comparing by hand, an `O(n)` scan the same shape as
`naive_rag`'s pre-`chromadb` retrieval. Lesson 21 moved the graph itself
onto `networkx`. This lesson finishes graduating the pipeline: node
lookup moves onto `chromadb` too, the same real vector database
`naive_rag` Lesson 20 introduced, so starting-node selection scales the
same way real similarity search does, and traversal runs on `networkx`
from there. This is Graph RAG's actual production shape: a vector
index for "where do I start," a graph for "what do I gather."

## Why this combination, and not one or the other alone

You might assume, having reached the Advanced tier, that a real vector
database has made the graph unnecessary, `chromadb` alone could just
retrieve the best-matching chunks the way `naive_rag` always has. Lesson
2 already showed why that's wrong for this course's own questions: no
amount of similarity-ranked chunks solves a question whose answer needs
a *relationship* between two low-overlap facts. The reverse assumption
is just as wrong: a graph alone, with no fast way to find where to
start on a large corpus, is stuck doing what Lesson 19 already showed
degrades badly at scale. Combining them plays each to its strength:
`chromadb` finds the entry point fast, at any corpus size; `networkx`
finds what connects to it, something no vector index does at all.

## The code, piece by piece

```python
collection = chroma_client.create_collection(name="graph_nodes")
node_names = list(graph.nodes())
collection.add(
    ids=node_names,
    documents=node_names,
    embeddings=embed_texts(node_names),
)
```

Every graph node gets indexed into `chromadb`, exactly like `naive_rag`
indexes document chunks, except what's being indexed here is *entity
names*, not passages of prose. This is the same idea Lesson 10 already
introduced, now backed by a real, indexed vector database instead of a
manual similarity scan over a Python list.

```python
def find_starting_node(query: str, collection: chromadb.Collection) -> str:
    query_vector = embed_texts([query])[0]
    results = collection.query(query_embeddings=[query_vector], n_results=1)
    return results["ids"][0][0]
```

`chromadb`'s own `query` method replaces Lesson 10's hand-rolled
cosine-similarity loop, the exact same swap `naive_rag` Lesson 21 made
for chunk retrieval.

```python
start = find_starting_node(query, collection)
facts = gather_facts(graph, start, max_hops=4)  # Lesson 21's networkx traversal, unchanged
```

The hybrid step itself: a `chromadb` query hands off to a `networkx`
traversal, two different retrieval mechanisms, chained through one
plain string, the starting node's name.

## Running it

```bash
uv run python lessons/graph_rag/03_advanced/22_graph_and_chromadb_hybrid_retrieval/lesson.py
```

## Expected output

```
Question: Who recalibrated the sensor that Dev flagged as drifting in the greenhouse, and what tool did they use?

Starting node (via chromadb query): 'greenhouse'

Answer:
...the facts show that Mia recalibrated a humidity sensor..., while Dev
posted about a humidity sensor. The tools associated with Mia include a
multimeter (which Mia pulled), but the facts do not explicitly connect
a specific tool directly to the act of recalibration.
```

`chromadb`'s embedding match for "greenhouse" can land a few hops
further from the eventual answer than a hand-picked start like
"humidity sensor" would (Lesson 21 started there directly), since real
similarity search finds the best-matching *entity*, not necessarily the
most central one for a given question's answer. This lesson uses a
slightly larger hop budget (4, not Lesson 21's 2) for exactly that
reason, and the answer may still hedge on details, like which tool was
used for the recalibration specifically, that require more hops than
even that to pin down precisely.

## Checkpoint

- **Graph + vector hybrid retrieval**: a vector index locates the
  starting entity fast at any scale; graph traversal gathers what
  connects to it, something a vector index alone can't do.
- Indexing entity *names* into `chromadb` (rather than chunks of prose)
  is the same tool, pointed at a different kind of content.
- This is the architecture's actual production shape: neither vector
  search nor graph traversal alone, both, each doing the part it's
  actually good at.

**Try this yourself:** index the graph's *edges* into `chromadb` too
(as short sentences, `f"{subject} {relation} {object}"`), alongside the
node index. Query that edge index directly with this lesson's question,
does the single best-matching edge alone come close to a full answer,
or does it still need traversal around it for the rest of the story?

If anything here still feels unclear, ask before moving to Lesson 23.
