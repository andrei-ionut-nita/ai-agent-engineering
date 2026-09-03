# Lesson 20: Introducing `networkx`

## Where we left off

Lesson 19 measured exactly where a hand-rolled dict-of-lists graph
starts to strain: pairwise operations like normalization grow
quadratically, and real graph questions (shortest path, connected
components) have no efficient answer in a plain dict at all. This
lesson introduces `networkx`, a pure-Python graph library, no server, no
extra account, just `pip install networkx` (already pulled in as a
dependency of other packages this repo uses, and made explicit in
`pyproject.toml` as of this lesson).

## What `networkx` actually is, given what you already built

This is worth saying plainly: `networkx` is not a new idea, it's a
better-engineered version of exactly what Lessons 5-6 built by hand.
Nodes, edges, and adjacency lookups, same concepts, same shape,
implemented with real indexing structures and a large library of
graph algorithms (shortest path, connected components, centrality, and
more) that would each take real effort to write correctly by hand.
Recognizing `add_edge` as "the thing I already wrote in Lesson 5" is the
whole point of having built it by hand first.

```python
import networkx as nx

G = nx.DiGraph()
G.add_edge("Mia", "humidity sensor", relation="recalibrated")
```

`nx.DiGraph()` is a **directed** graph, edges point one way, matching
exactly the `(subject, relation, object)` shape this course has used
since Lesson 4. `add_edge` takes the two endpoints directly and any
extra data (here, the relation label) as a keyword argument stored on
the edge, functionally identical to Lesson 5's `add_edge(graph,
subject, relation, obj)`, just backed by a proper graph data structure
instead of a dict of lists.

## What you get for free that you didn't have to write

```python
list(G.successors("Mia"))          # Lesson 6's one_hop, direct neighbors
list(nx.descendants(G, "Mia"))     # every node reachable at any depth
nx.shortest_path(G, "Mia", "greenhouse")  # a real algorithm, not hand-rolled
```

`successors` is Lesson 6's `one_hop`, one method call. `descendants` is
something this course's hand-rolled graph never actually implemented,
every node reachable from a starting point, at *any* depth, computed
efficiently. `shortest_path` answers a question this course has never
been able to ask at all: not "what's within two hops," but "what's the
*shortest* connection between these two specific nodes, however many
hops that takes."

## Running it

```bash
uv run python lessons/graph_rag/03_advanced/20_introducing_networkx/lesson.py
```

## Expected output

```
Mia's direct neighbors: ['humidity sensor', 'multimeter', 'smoke detectors']
All nodes reachable from Mia (any depth): ['electronics bench', 'greenhouse', 'humidity sensor', 'multimeter', 'smoke detectors']
Shortest path, Mia -> greenhouse: ['Mia', 'humidity sensor', 'greenhouse']
```

## Checkpoint

- `networkx`'s `DiGraph` is the same directed-graph idea Lessons 5-6
  built by hand, `add_edge` and `successors` map directly onto this
  course's own `add_edge` and `one_hop`.
- Real graph libraries earn their keep on operations this course's
  hand-rolled version never implemented at all: shortest path,
  reachability at any depth, and (used starting Lesson 22) proper
  indexing that avoids Lesson 19's `O(n²)` cost.
- Building the concept by hand first (Lessons 5-6) is what makes this
  lesson recognition, not new learning, exactly the same relationship
  `naive_rag` Lesson 20 (`chromadb`) has to that course's own
  hand-rolled vector store.

**Try this yourself:** build a small `DiGraph` from three or four
triples of your own choosing, then call `nx.shortest_path` between two
nodes that aren't directly connected. Trace the returned path by hand
against the edges you added, does it match what Lesson 6's two-hop
traversal would have found manually?

If anything here still feels unclear, ask before moving to Lesson 21.
