# Lesson 12: Multi-Document Graphs

## Where we left off

Every graph this course has built has technically already been a
multi-document graph, Lessons 8-11 all extract from every fixture note
and merge the results into one shared structure. This lesson names that
pattern explicitly and examines what "merging" really means, and where
it can go subtly wrong, because up to now it's been happening
implicitly inside `build_graph`, without ever being the actual subject
of a lesson.

## What merging documents into one graph actually requires

You might assume merging is just "run extraction on every file, dump
all the triples into one big list." That's necessary, but Lesson 11
already showed it's not sufficient on its own: two documents can name
the same entity differently, and without normalization those triples
land in *different* nodes even after merging. Multi-document merging is
really two separate jobs stacked together: **combining** (gather every
triple from every source) and **reconciling** (make sure triples about
the same real thing end up on the same node), and it's easy to do the
first while forgetting the second even exists as a separate step.

## The code, piece by piece

```python
def build_graph_with_provenance(notes_dir: Path) -> tuple[Graph, dict[str, set[str]]]:
    graph: Graph = {}
    provenance: dict[str, set[str]] = {}
    for path in sorted(notes_dir.glob("*.md")):
        for subject, relation, obj in extract_relationships(path.read_text()):
            add_edge(graph, subject, relation, obj)
            provenance.setdefault(subject, set()).add(path.name)
            provenance.setdefault(obj, set()).add(path.name)
    return graph, provenance
```

This is Lesson 8's `build_graph`, with one addition: a `provenance` dict
tracking which source file(s) mentioned each node. This isn't cosmetic,
it's what makes a node like `"electronics bench"` visibly a
*multi-document* node: check `provenance["electronics bench"]` and
you'll see it was mentioned in both `electronics-bench.md` and (once
Lesson 11's normalization runs) `maintenance-log.md`, direct, printable
proof that merging actually connected two separate documents' content
into one node, not just two lists concatenated side by side.

## Running it

```bash
uv run python lessons/graph_rag/02_intermediate/12_multi_document_graphs/lesson.py
```

## Expected output

```
Total nodes: 47 (after normalizing electronics/garage bench)
Nodes mentioned in more than one document:
  'electronics bench': {'electronics-bench.md', 'maintenance-log.md'}
  'humidity sensor': {'greenhouse.md', 'maintenance-log.md'}
  ...

'humidity sensor' is a genuine cross-document bridge: traversal
starting anywhere in greenhouse.md can reach facts that live only in
maintenance-log.md, and vice versa, because both documents' extraction
landed on the same node.
```

## Checkpoint

- Multi-document graph construction is combining (gather every triple)
  plus reconciling (Lesson 11's normalization), not combining alone.
- Tracking provenance (which source file(s) mentioned each node) turns
  "the graph merged documents" from an assumption into something you
  can actually verify, node by node.
- A node mentioned in more than one document is exactly the kind of
  bridge multi-hop traversal depends on, this is the concrete,
  inspectable version of the abstract claim Lessons 1-2 made about why
  graphs beat similarity search on multi-hop questions.

**Try this yourself:** find a node in this lesson's provenance dict that
appears in exactly one document. Pick one, and check by hand whether any
question could reasonably need to traverse *through* it to reach a fact
in a different document. What does that tell you about which nodes
matter most for multi-hop questions, the ones many documents mention,
or the ones exactly one document happens to mention?

If anything here still feels unclear, ask before moving to Lesson 13.
