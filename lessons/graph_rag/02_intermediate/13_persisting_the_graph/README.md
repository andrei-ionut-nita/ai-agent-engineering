# Lesson 13: Persisting the Graph to Disk

## Where we left off

Every lesson so far has paid the same tax on every single run: extract
entities and relationships from all six fixture files, from scratch,
every time, before the graph can answer even one question. That's six
Gemini calls of pure setup cost before any actual question gets asked,
paid again and again, even when the underlying documents haven't
changed since the last run. This lesson removes that tax: build the
graph once, save it to disk as JSON, and load it back on every
subsequent run instead of re-extracting.

## Why this is the same idea as `naive_rag` Lesson 13, just for a graph

`naive_rag` Lesson 13 saved embeddings to JSON instead of re-embedding
every run, for exactly this reason: embedding is expensive (API calls,
rate limits, latency) and the underlying text doesn't change between
runs, so there's no reason to redo work whose result would come out
identical. Extraction is the graph's equivalent expensive step, and the
same argument applies with equal force, arguably more force, since
extraction here means *six* separate structured-output calls per run,
not one batched embedding call.

## Why JSON, and what actually needs saving

You might assume the whole `Graph` type, a `dict[str, list[tuple[str,
str]]]`, can be dumped straight to JSON with `json.dump`. Almost:
JSON has no tuple type, only lists, so a value like `[("recalibrated",
"humidity sensor")]` round-trips through JSON as
`[["recalibrated", "humidity sensor"]]`, a list of two-element lists,
not tuples. This is a small but real gotcha: code that expects to
unpack `relation, other = edge` after loading needs to convert those
lists back into tuples explicitly, JSON doesn't do it for you, and
skipping that step produces a graph that *looks* right when printed but
breaks the moment traversal tries to unpack an edge.

## The code, piece by piece

```python
def save_graph(graph: Graph, path: Path) -> None:
    path.write_text(json.dumps(graph, indent=2))


def load_graph(path: Path) -> Graph:
    raw = json.loads(path.read_text())
    return {node: [tuple(edge) for edge in edges] for node, edges in raw.items()}
```

`save_graph` is almost trivial, dicts of lists are already
JSON-native. `load_graph` is where the tuple gotcha above actually gets
handled: the dict-comprehension's `tuple(edge)` is doing real, necessary
work, not just tidiness.

```python
if GRAPH_PATH.exists():
    graph = load_graph(GRAPH_PATH)
    print("Loaded graph from disk, no extraction needed.")
else:
    graph = build_graph(NOTES_DIR)
    save_graph(graph, GRAPH_PATH)
    print("Built graph from scratch and saved it.")
```

The pattern itself: check for a saved copy first, only pay the
extraction cost if one doesn't exist yet. Run this lesson twice in a row
and watch the second run skip extraction entirely, the same "build
once, reuse many times" shape this entire course has been building
toward since Lesson 8.

## Running it

```bash
uv run python lessons/graph_rag/02_intermediate/13_persisting_the_graph/lesson.py
```

## Expected output

First run:
```
Built graph from scratch and saved it.
Graph has 45 nodes, saved to graph.json.
```

Second run (delete nothing in between):
```
Loaded graph from disk, no extraction needed.
Graph has 45 nodes, saved to graph.json.
```

(Exact node count can shift slightly with extraction variance.)

## Checkpoint

- Persisting a graph means saving the extracted structure, not the
  source documents, once extraction has already turned prose into
  triples, there's no reason to pay for that conversion again on every
  run.
- JSON has no tuple type; loading a persisted graph needs to explicitly
  convert lists back into tuples, or code written to unpack edges as
  tuples will break.
- This is the exact same "build once at startup, don't rebuild per
  request" shape `naive_rag` Lesson 13 introduced, essential once
  Lesson 24 wraps this course's pipeline as a long-running service.

**Try this yourself:** delete `graph.json` and edit one fixture note
(add a sentence to `book-club.md`). Run this lesson once to rebuild and
save, then look at the saved file directly, can you find the new
sentence's effect on the graph just by reading the JSON?

If anything here still feels unclear, ask before moving to Lesson 14.
