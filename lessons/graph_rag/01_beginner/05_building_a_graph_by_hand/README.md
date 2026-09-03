# Lesson 5: Building a Graph by Hand

## Where we left off

Lesson 4 produced a flat list of triples, `("Mia", "recalibrated",
"humidity sensor")` and others like it. A list is still not a graph you
can *traverse*, though: to answer "what did Mia do?" from a plain list,
you'd have to scan every triple checking whether its subject is "Mia."
That's fine for six triples, unbearable for six thousand. This lesson
turns the list into an actual graph structure built for fast lookup:
an **adjacency dict**.

## What an adjacency dict actually is

The whole idea, stripped to its essence, before any library involvement:
a graph is nothing more than a dictionary where each key is a node
(an entity), and each value is a list of the edges leading out of it.

```python
graph = {
    "Mia": [("recalibrated", "humidity sensor"), ("pulled", "multimeter")],
    "humidity sensor": [("located in", "greenhouse")],
    ...
}
```

That's it. No special library, no database, this is exactly what
`networkx` (introduced much later, in the Advanced tier) does
underneath, just with more features bolted on. Building it by hand
first means that when Lesson 20 finally imports `networkx`, you'll
recognize `add_edge` as doing something you've already done yourself,
not a mysterious black box.

## Why store both directions

```python
def add_edge(graph, subject, relation, obj):
    graph.setdefault(subject, []).append((relation, obj))
    graph.setdefault(obj, []).append((f"(reverse) {relation}", subject))
```

You might assume storing `("Mia", "recalibrated", "humidity sensor")`
once is enough, since the fact is fully captured. It's captured, but not
*reachable* from both ends. If a later traversal starts at "humidity
sensor" (because that's the entity found in the question), and the
edge only exists on `graph["Mia"]`, the traversal from "humidity
sensor" has no way to discover Mia at all, real relationships go two
directions, even when the sentence describing them only reads in one.
Storing the reverse edge too, labeled distinctly so it doesn't get
confused with a real forward relation, is what makes traversal work
starting from *either* endpoint, which matters a lot once Lesson 6
starts traversing from whatever entity a question happens to mention
first.

## The code, piece by piece

```python
graph: dict[str, list[tuple[str, str]]] = {}
for subject, relation, obj in triples:
    add_edge(graph, subject, relation, obj)
```

Nothing surprising: walk the triples from Lesson 4, add each one (and
its reverse) into the dict. `setdefault(subject, [])` is doing the
"create this key if it doesn't exist yet" work a `defaultdict` would
also do, spelled out explicitly here since this course hasn't
introduced `defaultdict` yet and the goal is maximum transparency over
what's happening.

## Running it

```bash
uv run python lessons/graph_rag/01_beginner/05_building_a_graph_by_hand/lesson.py
```

## Expected output

```
Nodes in the graph: ['Mia', 'humidity sensor', 'multimeter', 'greenhouse', 'garage bench', ...]

Mia's edges:
  recalibrated -> humidity sensor
  pulled -> multimeter
  replaced batteries in -> smoke detectors

humidity sensor's edges:
  (reverse) recalibrated -> Mia
  (reverse) flagged -> Dev
  located in -> greenhouse
```

Exact edges and their exact wording vary slightly run to run, inherited
directly from Lesson 4's extraction variance, one run might phrase an
edge as `located in -> greenhouse` and the next as `is in -> greenhouse
(part of a project)`. What should stay consistent: Mia's node reliably
includes an edge to the humidity sensor, and the humidity sensor's node
reliably includes a reverse edge back to Mia.

## Checkpoint

- **Adjacency dict**: a graph represented as `{node: [(relation, other_node), ...]}`,
  the simplest possible traversable graph structure.
- Storing the reverse of every edge is what makes a node reachable
  regardless of which end of the relationship a traversal starts from.
- This by-hand structure is functionally what `networkx.DiGraph` does
  underneath, this course builds it manually first so the library,
  introduced later, is recognizable rather than magic.

**Try this yourself:** add a triple by hand, `("Priya", "borrowed",
"soldering station")`, to the graph this lesson builds, then look up
`graph["soldering station"]`. Does it correctly show Priya as one of
the entities connected to it, even though the triple was written with
Priya as the subject, not the object?

If anything here still feels unclear, ask before moving to Lesson 6.
