# Lesson 19: Where a Hand-Rolled Graph Breaks Down

## Where we left off

Every graph this course has built is a plain Python `dict[str,
list[tuple[str, str]]]`, and every traversal has been a couple of
nested loops. That's been completely fine at this course's scale, about
fifty nodes across six fixture files. This lesson does what `naive_rag`
Lesson 19 did for its own hand-rolled vector store: time the hand-rolled
graph as it grows, and find out exactly where "completely fine" stops
being true.

## Why a dict-of-lists graph doesn't scale gracefully

You might assume a dictionary lookup is always fast, `O(1)`, so a graph
built entirely from dictionary lookups should scale fine no matter how
big it gets. The lookup itself does stay fast. What doesn't stay fast is
everything *around* the lookup that this course's code has been doing
casually: Lesson 11's normalization compares every node name to every
other node name, an `O(n²)` operation, at fifty nodes that's about
1,225 comparisons, trivial; at fifty thousand nodes, that's over a
billion, no longer trivial at all. Traversal itself has a subtler
problem: nothing in this course's `gather_facts` has ever needed a
shortest-path query, a "does a path exist between these two nodes even
without knowing it in advance" query, or a "which nodes are most
connected" query, all real questions a bigger graph inevitably needs
answered, and all things a hand-rolled dict has no efficient way to
compute without writing real graph algorithms from scratch.

## The code, piece by piece

```python
def make_synthetic_graph(num_nodes: int, edges_per_node: int) -> Graph:
    graph: Graph = {}
    for i in range(num_nodes):
        node = f"node-{i}"
        for _ in range(edges_per_node):
            other = f"node-{random.randint(0, num_nodes - 1)}"
            add_edge(graph, node, "connects to", other)
    return graph
```

A synthetic graph, not extracted from real text, built purely to time
graph *operations* at sizes this course's real fixture set will never
reach. This is the same technique `naive_rag` Lesson 19 used for timing
a synthetic vector store: the point isn't the specific fake data, it's
watching an operation's cost curve as size grows.

```python
start = time.perf_counter()
find_merge_candidates_naive(graph)  # O(n^2) pairwise comparison
elapsed = time.perf_counter() - start
```

Timing Lesson 11's own normalization approach directly, at increasing
graph sizes, to watch its `O(n²)` cost curve stop being "trivial" and
start being "slow enough to notice."

## Running it

```bash
uv run python lessons/graph_rag/03_advanced/19_where_hand_rolled_graphs_break_down/lesson.py
```

## Expected output

```
Nodes: 100     Pairwise comparisons: 4,950        Time: 0.0001s
Nodes: 1,000   Pairwise comparisons: 499,500      Time: 0.0158s
Nodes: 5,000   Pairwise comparisons: 12,497,500   Time: 0.4470s
Nodes: 20,000  Pairwise comparisons: 199,990,000  Time: 8.5946s
```

Exact timings depend on your machine, the shape is the point: every 5x
increase in nodes costs roughly 25x in comparisons, quadratic growth,
not the roughly-linear growth this course's traversal itself has shown
so far. Normalization, run once per new document ingested, becomes the
actual bottleneck long before traversal does.

## Checkpoint

- A hand-rolled adjacency dict handles single-node lookups and simple
  traversal fine at any size, `O(1)` dictionary access doesn't degrade.
- What breaks first is *pairwise* operations like Lesson 11's
  normalization, `O(n²)` cost that becomes genuinely slow well before
  the node count gets dramatic.
- Real graph libraries solve this with proper indexing structures and
  well-tested algorithms (shortest path, connected components,
  centrality) this course's dict-of-lists never implemented at all,
  not just faster versions of what's already here.

**Try this yourself:** before reading Lesson 20, guess what data
structure a real graph library like `networkx` uses internally to avoid
the `O(n²)` normalization cost this lesson just measured. Is it a
smarter comparison algorithm, or a smarter way to avoid comparing every
pair at all (a hint: think about how Lesson 10 already avoids comparing
a query to every single chunk in `naive_rag`'s vector database once
that database gets big, via approximate nearest-neighbor structures)?

If anything here still feels unclear, ask before moving to Lesson 20.
