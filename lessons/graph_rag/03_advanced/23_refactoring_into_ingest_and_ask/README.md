# Lesson 23: Refactoring Into `ingest()` and `ask()`

## Where we left off

Every Advanced-tier lesson so far has been one script, top to bottom:
build a graph, index it, answer one question, done. This lesson
reshapes that into the same two-function boundary `naive_rag` Lesson 23
established: `ingest()`, run once, does all the expensive setup;
`ask()`, run per question, answers using whatever `ingest()` built.
That boundary matters for a concrete reason, covered directly below:
it's what makes Lesson 24's web service, and later, this whole series'
`adaptive_rag` course, able to use this course's pipeline without
reading its internals.

## The shared `Strategy` protocol, and what lives in this course's `State`

This repo's RAG-architecture series shares one convention across every
course's own Lesson 23 (`docs/RAG-SERIES-PLAN/README.md`'s "Shared
Strategy Protocol"):

```python
class Strategy(Protocol):
    def ingest(self, docs: list[Path]) -> object: ...   # returns opaque State
    def ask(self, query: str, state: object, k: int = 2) -> str: ...
```

For this course, `State` is a `NamedTuple` with exactly two fields:

```python
class State(NamedTuple):
    graph: nx.DiGraph
    collection: chromadb.Collection
```

`graph` holds every extracted `(subject, relation, object)` triple,
Lesson 21's `networkx` structure. `collection` holds the `chromadb`
index of graph node names, Lesson 22's vector index used to find a
traversal's starting point. Nothing else lives in `State`, generation
doesn't need its own persisted state, `ask()` calls Gemini fresh every
time it runs, the same way every earlier lesson in this course has.
Any other course in this series wiring this one in (see
`adaptive_rag` Lesson 21) only needs these two fields and this file's
two function signatures, not this file's internals.

## The code, piece by piece

```python
def ingest(docs: list[Path]) -> State:
    graph = nx.DiGraph()
    for path in docs:
        for subject, relation, obj in extract_relationships(path.read_text()):
            graph.add_edge(subject, obj, relation=relation)

    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="graph_nodes")
    node_names = list(graph.nodes())
    collection.add(ids=node_names, documents=node_names, embeddings=embed_texts(node_names))

    return State(graph=graph, collection=collection)
```

Everything Lessons 21-22 called "build the graph, then index it"
collapses into this one function. Anything that needs a ready-to-query
Graph RAG pipeline calls this once and gets a `State` back, no other
function in this course needs to know how that state was built.

```python
def ask(query: str, state: State, k: int = 2) -> str:
    query_vector = embed_texts([query])[0]
    results = state.collection.query(query_embeddings=[query_vector], n_results=1)
    start = results["ids"][0][0]

    facts = gather_facts(state.graph, start, max_hops=3)
    return generate_answer(query, facts)
```

Everything Lessons 15 and 22 called "find a start, traverse, generate"
collapses into this one function. `k` is part of the shared protocol's
signature; this course's traversal doesn't use it directly (traversal
depth is fixed by Lesson 14's tuning, not by `k`), it's accepted for
interface compatibility with every other course's `ask()`, the same way
a function argument can exist for a caller's benefit even when this
particular implementation doesn't vary its behavior on it.

## Running it

```bash
uv run python lessons/graph_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py
```

## Expected output

```
Ingested a graph with 47 nodes.

Q: What's stored on the garage electronics bench?
A: <a grounded answer listing items on the bench, e.g. soldering station,
   parts bin, Raspberry Pi, multimeter, jumper wires>

Q: What is the capital of France?
A: Based on the provided facts, there is no mention of the capital of France.
```

(Exact node count shifts slightly with extraction variance.)

## Checkpoint

- **`State`**: this course's opaque state object, a `NamedTuple` of
  `(graph, collection)`, a `networkx.DiGraph` and a `chromadb.Collection`.
- `ingest(docs) -> State` and `ask(query, state, k=2) -> str` match this
  series' shared `Strategy` protocol exactly, the same two-function
  shape `naive_rag` Lesson 23 established as the reference
  implementation.
- Any later course composing multiple strategies (`adaptive_rag`) can
  wire this course in using only this lesson's two signatures, without
  reading Lessons 1-22.

**Try this yourself:** write a third question whose answer needs
`k` to matter, if you can think of one for this architecture. If you
can't, explain in your own words why traversal depth, not `k`, is the
knob that actually controls how much context Graph RAG's `ask()`
gathers, unlike `naive_rag`'s `ask()`, where `k` is the primary knob.

If anything here still feels unclear, ask before moving to Lesson 24.
