"""
Lesson 19: timing a hand-rolled adjacency-dict graph's O(n^2)
normalization cost as the node count grows, to find exactly where it
stops being trivial.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/03_advanced/19_where_hand_rolled_graphs_break_down/lesson.py

No Gemini calls in this lesson, it's pure Python timing, no API key
required.
"""

import random
import time

Graph = dict[str, list[tuple[str, str]]]


def add_edge(graph: Graph, subject: str, relation: str, obj: str) -> None:
    graph.setdefault(subject, []).append((relation, obj))
    graph.setdefault(obj, []).append((f"(reverse) {relation}", subject))


def make_synthetic_graph(num_nodes: int, edges_per_node: int = 3) -> Graph:
    random.seed(0)
    graph: Graph = {}
    for i in range(num_nodes):
        node = f"node-{i}"
        graph.setdefault(node, [])
        for _ in range(edges_per_node):
            other = f"node-{random.randint(0, num_nodes - 1)}"
            add_edge(graph, node, "connects to", other)
    return graph


def time_pairwise_comparison(graph: Graph) -> tuple[int, float]:
    # Simulates Lesson 11's normalization step: compare every node name
    # to every other node name. Uses string length as a cheap stand-in
    # for a real similarity score, since the point here is timing the
    # O(n^2) loop shape itself, not embedding accuracy.
    node_names = list(graph.keys())
    comparisons = 0
    start = time.perf_counter()
    for i in range(len(node_names)):
        for j in range(i + 1, len(node_names)):
            _ = abs(len(node_names[i]) - len(node_names[j]))
            comparisons += 1
    elapsed = time.perf_counter() - start
    return comparisons, elapsed


def main() -> None:
    for num_nodes in (100, 1_000, 5_000, 20_000):
        graph = make_synthetic_graph(num_nodes)
        comparisons, elapsed = time_pairwise_comparison(graph)
        print(
            f"Nodes: {num_nodes:<7,} Pairwise comparisons: {comparisons:<12,} "
            f"Time: {elapsed:.4f}s"
        )


if __name__ == "__main__":
    main()
