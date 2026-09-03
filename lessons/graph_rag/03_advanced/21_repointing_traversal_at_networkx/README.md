# Lesson 21: Re-Pointing Extraction and Traversal at `networkx`

## Where we left off

Lesson 20 introduced `networkx` in isolation, a few hand-written
triples, no extraction involved. This lesson does what `naive_rag`
Lesson 21 did when it swapped a hand-rolled vector store for
`chromadb`: point this course's *real* pipeline, Lesson 3's extraction
into Lesson 7's traversal, at `networkx` instead of the hand-rolled
dict, with the same interface every earlier lesson has used, so
everything built on top of it (citation generation, Lesson 15; the
checkpoint CLI, Lesson 18) doesn't need to change at all.

## Why "same interface" is the actual design goal here

You might assume swapping the graph backend means rewriting
`gather_facts`, `generate_answer`, and everything downstream. It
doesn't, and that's deliberate: `build_graph` still takes a folder of
notes and returns something traversable; `gather_facts` still takes a
graph and a starting node and returns a list of fact strings. What
changes is only what's *inside* those functions, a `networkx.DiGraph`
instead of a `dict`, `graph.successors(node)` instead of
`graph.get(node, [])`. This mirrors exactly how `naive_rag`'s `ingest`
and `retrieve` functions kept the same signatures across Lessons 5, 13,
and 21 even as their internals moved from a Python list to JSON on
disk to `chromadb`. A well-chosen interface is what makes a backend
swap a one-file change instead of a cascading rewrite.

## The code, piece by piece

```python
def build_graph(notes_dir: Path) -> nx.DiGraph:
    graph = nx.DiGraph()
    for path in sorted(notes_dir.glob("*.md")):
        for subject, relation, obj in extract_relationships(path.read_text()):
            graph.add_edge(subject, obj, relation=relation)
    return graph
```

`extract_relationships` (Lesson 4, unchanged) still does the extraction
work. `build_graph`'s *shape* is unchanged too, loop over files, loop
over triples, add each one, only the last line's mechanics differ:
`graph.add_edge(subject, obj, relation=relation)` instead of Lesson 5's
`add_edge(graph, subject, relation, obj)`. Note there's no manual
reverse-edge bookkeeping here either, `networkx` gives you `predecessors`
for that direction directly, Lesson 5's `(reverse) {relation}` labeling
trick was a hand-rolled workaround for something the library already
provides properly.

```python
def gather_facts(graph: nx.DiGraph, start: str, max_hops: int = 2) -> list[str]:
    facts = []
    frontier = {start}
    visited = {start}
    for _ in range(max_hops):
        next_frontier = set()
        for node in frontier:
            for _, other, data in graph.out_edges(node, data=True):
                facts.append(f"{node} {data['relation']} {other}")
                if other not in visited:
                    next_frontier.add(other)
                    visited.add(other)
            for other, _, data in graph.in_edges(node, data=True):
                facts.append(f"{other} {data['relation']} {node}")
                if other not in visited:
                    next_frontier.add(other)
                    visited.add(other)
        frontier = next_frontier
    return facts
```

Structurally identical to Lesson 7's `gather_facts`, frontier-based,
hop-limited, same signature. The one real change: `out_edges` and
`in_edges` replace the hand-rolled forward/reverse edge storage
Lesson 5 needed, `networkx` already indexes both directions
internally, so nothing needs to be duplicated at insert time the way
Lesson 5's `add_edge` duplicated every edge into two dict entries.

## Running it

```bash
uv run python lessons/graph_rag/03_advanced/21_repointing_traversal_at_networkx/lesson.py
```

## Expected output

```
Question: Who recalibrated the sensor that Dev flagged as drifting in the greenhouse, and what tool did they use?

Answer:
Based on the provided facts, Mia recalibrated the humidity sensor. However,
the facts do not mention the sensor drifting in a greenhouse, nor do they
specify what tool she used for the recalibration (though a separate fact
mentions that she pulled a multimeter).
```

Compare this file's line count and logic against Lesson 7's: functions
keep the same names, the same signatures, and mostly the same bodies.
The backend swap changed maybe a dozen lines total.

## Checkpoint

- Swapping a graph's backend implementation, dict to `networkx`,
  doesn't require touching extraction or generation code, if the
  interface (`build_graph`, `gather_facts`) stayed stable across the
  swap.
- `networkx` indexes both edge directions natively; Lesson 5's manual
  `(reverse) {relation}` bookkeeping was a hand-rolled stand-in for
  something the real library already handles.
- This is the same lesson `naive_rag` Lesson 21 taught for `chromadb`:
  a good interface, chosen early, is what makes graduating to a real
  library a small, mechanical change instead of a redesign.

**Try this yourself:** delete this lesson's `in_edges` loop from
`gather_facts` and rerun. Does the humidity-sensor question still get
answered correctly? What does that tell you about which direction most
of this course's fixture graph's useful connections actually run?

If anything here still feels unclear, ask before moving to Lesson 22.
