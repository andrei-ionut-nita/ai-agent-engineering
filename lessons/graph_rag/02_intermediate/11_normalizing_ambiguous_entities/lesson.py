"""
Lesson 11: merging graph nodes that refer to the same real-world thing
but were extracted under different names, using embedding similarity.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/02_intermediate/11_normalizing_ambiguous_entities/lesson.py
"""

import json
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"
EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

# Chosen by observing this course's own graph: "electronics bench" and
# "garage bench" score ~0.79, every genuinely different pair of node
# names scores well under 0.6.
MERGE_THRESHOLD = 0.75

Graph = dict[str, list[tuple[str, str]]]


def extract_relationships(text: str) -> list[tuple[str, str, str]]:
    prompt = f"""You are extracting relationships for a knowledge graph.

Read the text below and list EVERY relationship between two entities as
a (subject, relation, object) triple, including actions one entity took
regarding another (e.g. "flagged as drifting", "noticed", "pulled",
"recalibrated"), not just static facts. Be thorough: aim for at least
one triple per sentence that mentions two or more entities.

When a sentence describes an action about something already named
earlier in the text, use that thing's established full name as the
subject or object, not a pronoun, a paraphrase, or an abstract noun
like "drift" or "the issue." For example, if "the humidity sensor" was
already introduced, "Dev flagged it as drifting" should produce
("Dev", "flagged as drifting", "humidity sensor"), not
("Dev", "flagged", "drift").

The subject and object should be short entity names (people, places,
specific things), and the relation should be a short verb phrase
(2-4 words).

Return ONLY a JSON array of 3-element arrays, like:
[["Mia", "recalibrated", "humidity sensor"], ["multimeter", "kept in", "garage bench"]]

Text:
{text}"""
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json", temperature=0
        ),
    )
    assert response.text is not None
    triples = json.loads(response.text)
    return [tuple(triple) for triple in triples]


def add_edge(graph: Graph, subject: str, relation: str, obj: str) -> None:
    graph.setdefault(subject, []).append((relation, obj))
    graph.setdefault(obj, []).append((f"(reverse) {relation}", subject))


def build_graph(notes_dir: Path) -> Graph:
    graph: Graph = {}
    for path in sorted(notes_dir.glob("*.md")):
        for subject, relation, obj in extract_relationships(path.read_text()):
            add_edge(graph, subject, relation, obj)
    return graph


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    assert response.embeddings is not None
    return [e.values for e in response.embeddings if e.values is not None]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x * x for x in a) ** 0.5
    mag_b = sum(y * y for y in b) ** 0.5
    return dot / (mag_a * mag_b)


def find_merge_candidates(graph: Graph) -> list[tuple[str, str, float]]:
    node_names = list(graph.keys())
    node_vectors = embed_texts(node_names)
    candidates = []
    for i in range(len(node_names)):
        for j in range(i + 1, len(node_names)):
            score = cosine_similarity(node_vectors[i], node_vectors[j])
            if score >= MERGE_THRESHOLD:
                candidates.append((node_names[i], node_names[j], score))
    return candidates


def merge_nodes(graph: Graph, keep: str, drop: str) -> None:
    # Move the dropped node's own edges onto the node being kept.
    for relation, other in graph.pop(drop, []):
        graph.setdefault(keep, []).append((relation, other))
    # Rewrite every other node's edges so nothing still points at a
    # name that no longer exists in the graph.
    for node, edges in graph.items():
        graph[node] = [(rel, keep if other == drop else other) for rel, other in edges]


def main() -> None:
    graph = build_graph(NOTES_DIR)
    print(f"Nodes before normalizing: {len(graph)}")

    candidates = find_merge_candidates(graph)
    for name_a, name_b, score in candidates:
        # Keep the shorter, more general name.
        keep, drop = (name_a, name_b) if len(name_a) <= len(name_b) else (name_b, name_a)
        print(f"Merging: '{drop}' -> '{keep}' (similarity {score:.2f})")
        merge_nodes(graph, keep, drop)

    print(f"Nodes after normalizing: {len(graph)}\n")

    target = "electronics bench"
    print(f"Edges on '{target}' after normalizing:")
    for relation, other in graph.get(target, []):
        print(f"  {relation} -> {other}")


if __name__ == "__main__":
    main()
