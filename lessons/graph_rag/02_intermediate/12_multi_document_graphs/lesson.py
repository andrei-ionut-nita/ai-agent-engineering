"""
Lesson 12: building a graph from multiple documents while tracking
provenance (which source file(s) mentioned each node), and reconciling
duplicate entity names, the two halves multi-document merging needs.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/02_intermediate/12_multi_document_graphs/lesson.py
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

MERGE_THRESHOLD = 0.75

Graph = dict[str, list[tuple[str, str]]]
Provenance = dict[str, set[str]]


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


def build_graph_with_provenance(notes_dir: Path) -> tuple[Graph, Provenance]:
    graph: Graph = {}
    provenance: Provenance = {}
    for path in sorted(notes_dir.glob("*.md")):
        for subject, relation, obj in extract_relationships(path.read_text()):
            add_edge(graph, subject, relation, obj)
            provenance.setdefault(subject, set()).add(path.name)
            provenance.setdefault(obj, set()).add(path.name)
    return graph, provenance


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


def normalize(graph: Graph, provenance: Provenance) -> None:
    node_names = list(graph.keys())
    node_vectors = embed_texts(node_names)
    for i in range(len(node_names)):
        for j in range(i + 1, len(node_names)):
            if cosine_similarity(node_vectors[i], node_vectors[j]) < MERGE_THRESHOLD:
                continue
            name_a, name_b = node_names[i], node_names[j]
            if name_a not in graph or name_b not in graph:
                continue  # already merged into something else this pass
            keep, drop = (name_a, name_b) if len(name_a) <= len(name_b) else (name_b, name_a)
            for relation, other in graph.pop(drop, []):
                graph.setdefault(keep, []).append((relation, other))
            for node, edges in graph.items():
                graph[node] = [
                    (rel, keep if other == drop else other) for rel, other in edges
                ]
            provenance.setdefault(keep, set()).update(provenance.pop(drop, set()))


def main() -> None:
    graph, provenance = build_graph_with_provenance(NOTES_DIR)
    normalize(graph, provenance)

    print(f"Total nodes: {len(graph)}\n")

    print("Nodes mentioned in more than one document:")
    for node, sources in sorted(provenance.items()):
        if len(sources) > 1:
            print(f"  {node!r}: {sources}")


if __name__ == "__main__":
    main()
