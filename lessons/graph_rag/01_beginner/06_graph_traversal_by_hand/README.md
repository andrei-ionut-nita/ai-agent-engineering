# Lesson 6: Graph Traversal by Hand

## Where we left off

Lesson 5 built a graph, `{node: [(relation, other_node), ...]}`. A graph
sitting in memory doesn't answer anything by itself, it has to be
**traversed**: starting from one node, walking its edges to find
neighbors, then optionally walking *their* edges to find neighbors of
neighbors. This lesson writes that walk by hand, for one hop and for two.

## One-hop: direct neighbors

```python
def one_hop(graph: Graph, node: str) -> list[tuple[str, str]]:
    return graph.get(node, [])
```

This is nearly a one-liner because Lesson 5 already did the hard part:
since every node's edges are stored right there in the dict value,
finding a node's direct neighbors is just a dictionary lookup, not a
search. That's the entire payoff of building the adjacency structure
correctly: traversal, the thing this whole course is building toward,
turns out to be almost trivially cheap once the graph itself is right.

## Two-hop: neighbors of neighbors

```python
def two_hop(graph: Graph, node: str) -> list[tuple[str, str, str]]:
    results = []
    for relation1, neighbor in one_hop(graph, node):
        for relation2, neighbor2 in one_hop(graph, neighbor):
            results.append((relation1, neighbor, relation2, neighbor2))
    return results
```

Two-hop is one-hop applied twice: for every neighbor found in the first
hop, look up *its* neighbors too. This is where you might assume the
obvious next step is "so three-hop is just one more loop, and unbounded
hops is the most thorough option." Resist that assumption. Watch what
happens if you run two-hop starting from "multimeter" in this lesson's
output: at hop 2 the traversal reaches "garage bench," and at a
hypothetical hop 3 it would reach *everything else on that bench*,
including the soldering station Priya borrowed for an unrelated lamp
repair that has nothing to do with a humidity sensor question. Every
additional hop doesn't just add more *correct* context, it adds
exponentially more *tangential* context, most of it irrelevant to
whatever question sent the traversal there in the first place. Lesson
14 makes this precise; for now, just notice it happening.

## Why depth matters more here than `k` mattered in Naive RAG

In `naive_rag`, raising `k` costs you retrieval precision gradually,
one extra chunk at a time. In a graph, raising traversal depth costs you
precision combinatorially: if a node has five edges on average, one hop
reaches five nodes, two hops can reach up to twenty-five, three hops up
to a hundred twenty-five. This is why "just traverse further to be
safe" is actually a worse instinct in Graph RAG than "just raise k" was
in Naive RAG, the failure mode gets bigger, not smaller, as the fix gets
applied.

## Running it

```bash
uv run python lessons/graph_rag/01_beginner/06_graph_traversal_by_hand/lesson.py
```

## Expected output

```
One-hop from 'multimeter':
  kept in -> garage bench's top drawer
  (reverse) holds -> electronics bench

Two-hop from 'multimeter':
  (reverse) holds -> electronics bench -> (reverse) uses -> Mia
  (reverse) holds -> electronics bench -> (reverse) uses -> Dev
  (reverse) holds -> electronics bench -> holds -> soldering station
  (reverse) holds -> electronics bench -> holds -> spare Raspberry Pi
  ...
```

Notice the last two lines: neither the soldering station nor the spare
Raspberry Pi has anything to do with a humidity sensor question, they're
reachable purely because they happen to share a two-hop neighborhood
with the multimeter. That's not a bug in this lesson's code, it's the
real shape of unconstrained traversal, exactly what Lesson 14 exists to
fix.

## Checkpoint

- **Traversal**: walking a graph's edges outward from a starting node,
  one hop at a time.
- One-hop is a direct dictionary lookup; two-hop applies that lookup
  again to each neighbor found.
- Traversal depth grows the reachable set combinatorially, not linearly,
  so "traverse deeper to be thorough" backfires much faster than "raise
  k" ever did in Naive RAG.

**Try this yourself:** run two-hop starting from `"Mia"` instead of
`"multimeter"`. Does it reach `"Dev"`? Trace by hand which edges the
traversal must follow to get there, and whether that path passes
through a node that has nothing to do with either Mia or Dev directly.

If anything here still feels unclear, ask before moving to Lesson 7.
