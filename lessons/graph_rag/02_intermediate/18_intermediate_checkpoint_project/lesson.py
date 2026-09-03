"""
Lesson 18: Intermediate checkpoint. The Beginner CLI (Lesson 9),
upgraded with every Intermediate-tier idea: provenance-tracked
extraction, entity normalization, persistence, a tuned traversal depth,
embedding-based starting-node selection, and per-hop citations.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/02_intermediate/18_intermediate_checkpoint_project/lesson.py

Run it twice: the first run extracts and saves; the second loads.
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
GRAPH_PATH = Path(__file__).parent / "graph.json"

MERGE_THRESHOLD = 0.75
# Chosen in Lesson 14 by directly observing what each depth retrieves,
# not by tuning against a labeled evaluation set.
MAX_HOPS = 2

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
                continue
            keep, drop = (name_a, name_b) if len(name_a) <= len(name_b) else (name_b, name_a)
            for relation, other in graph.pop(drop, []):
                graph.setdefault(keep, []).append((relation, other))
            for node, edges in graph.items():
                graph[node] = [
                    (rel, keep if other == drop else other) for rel, other in edges
                ]
            provenance.setdefault(keep, set()).update(provenance.pop(drop, set()))


def save_graph(graph: Graph, provenance: Provenance, path: Path) -> None:
    payload = {
        "graph": graph,
        "provenance": {node: sorted(sources) for node, sources in provenance.items()},
    }
    path.write_text(json.dumps(payload, indent=2))


def load_graph(path: Path) -> tuple[Graph, Provenance]:
    raw = json.loads(path.read_text())
    graph = {node: [tuple(edge) for edge in edges] for node, edges in raw["graph"].items()}
    provenance = {node: set(sources) for node, sources in raw["provenance"].items()}
    return graph, provenance


def find_starting_node(query: str, graph: Graph) -> str:
    node_names = list(graph.keys())
    node_vectors = embed_texts(node_names)
    query_vector = embed_texts([query])[0]
    scores = [cosine_similarity(query_vector, v) for v in node_vectors]
    best_index = max(range(len(node_names)), key=lambda i: scores[i])
    return node_names[best_index]


def gather_facts_with_sources(
    graph: Graph, provenance: Provenance, start: str, max_hops: int
) -> list[tuple[str, set[str]]]:
    facts: list[tuple[str, set[str]]] = []
    frontier = {start}
    visited = {start}
    for _ in range(max_hops):
        next_frontier = set()
        for node in frontier:
            for relation, other in graph.get(node, []):
                sources = provenance.get(node, set()) & provenance.get(other, set())
                if not sources:
                    sources = provenance.get(node, set()) | provenance.get(other, set())
                facts.append((f"{node} {relation} {other}", sources))
                if other not in visited:
                    next_frontier.add(other)
                    visited.add(other)
        frontier = next_frontier
    return facts


def generate_cited_answer(query: str, facts: list[tuple[str, set[str]]]) -> str:
    context = "\n".join(
        f"{fact} [source: {', '.join(sorted(sources)) or 'unknown'}]" for fact, sources in facts
    )
    prompt = f"""You are answering a question using facts gathered by
traversing a knowledge graph. Each fact is tagged with the source
file(s) it came from. Build a coherent answer using only what the facts
support, and after each claim, cite the source file in square brackets,
like [greenhouse.md]. If a specific detail genuinely isn't supported by
any fact, say so plainly instead of guessing, and don't invent a
citation for it.

Facts:
{context}

Question: {query}"""
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def ask(query: str, graph: Graph, provenance: Provenance) -> str:
    start = find_starting_node(query, graph)
    facts = gather_facts_with_sources(graph, provenance, start, max_hops=MAX_HOPS)
    return generate_cited_answer(query, facts)


def main() -> None:
    if GRAPH_PATH.exists():
        graph, provenance = load_graph(GRAPH_PATH)
        print("Loaded graph from disk, no extraction needed.\n")
    else:
        graph, provenance = build_graph_with_provenance(NOTES_DIR)
        normalize(graph, provenance)
        save_graph(graph, provenance, GRAPH_PATH)
        print("Built graph from scratch, normalized it, and saved it.\n")

    questions = [
        "Who recalibrated the sensor that Dev flagged as drifting in the greenhouse, and what tool did they use?",
        "What earlier project inspired Dev's soil moisture sensor build?",
        "What tools are kept on the garage electronics bench?",
    ]

    for query in questions:
        print(f"Q: {query}")
        print(f"A: {ask(query, graph, provenance)}\n")


if __name__ == "__main__":
    main()
