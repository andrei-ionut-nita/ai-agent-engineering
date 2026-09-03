"""
Lesson 20: introducing networkx.DiGraph as a drop-in replacement for
the hand-rolled adjacency-dict graph built in Lessons 5-6.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/03_advanced/20_introducing_networkx/lesson.py

No Gemini calls in this lesson, a small hand-written set of triples is
enough to show networkx's mechanics, no API key required.
"""

import networkx as nx

TRIPLES = [
    ("Mia", "recalibrated", "humidity sensor"),
    ("Mia", "pulled", "multimeter"),
    ("Mia", "replaced batteries in", "smoke detectors"),
    ("humidity sensor", "located in", "greenhouse"),
    ("multimeter", "kept in", "electronics bench"),
    ("Dev", "flagged", "humidity sensor"),
    ("Dev", "uses", "electronics bench"),
]


def build_graph(triples: list[tuple[str, str, str]]) -> nx.DiGraph:
    graph = nx.DiGraph()
    for subject, relation, obj in triples:
        graph.add_edge(subject, obj, relation=relation)
    return graph


def main() -> None:
    graph = build_graph(TRIPLES)

    print(f"Mia's direct neighbors: {list(graph.successors('Mia'))}")
    print(
        "All nodes reachable from Mia (any depth): "
        f"{sorted(nx.descendants(graph, 'Mia'))}"
    )
    path = nx.shortest_path(graph, "Mia", "greenhouse")
    print(f"Shortest path, Mia -> greenhouse: {path}")


if __name__ == "__main__":
    main()
