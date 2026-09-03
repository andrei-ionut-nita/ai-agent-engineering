"""
Lesson 17: precision@k, chunk-based retrieval vs. graph-based retrieval,
on a small labeled set of multi-hop questions.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/02_intermediate/17_minimal_evaluation_chunk_vs_graph/lesson.py
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

Graph = dict[str, list[tuple[str, str]]]
Provenance = dict[str, set[str]]

# Each question was built so the two needed documents share almost no
# vocabulary with each other, connected only through a shared entity,
# exactly the shape chunk-based retrieval structurally struggles with.
LABELED_QUESTIONS: list[tuple[str, set[str]]] = [
    (
        "Who recalibrated the sensor that Dev flagged as drifting, and what tool did they use?",
        {"greenhouse.md", "maintenance-log.md"},
    ),
    (
        "What project inspired Dev's soil moisture sensor, and in which room does that project happen?",
        {"soil-moisture-project.md", "workshop.md"},
    ),
    (
        "Which piece of equipment does Dev's soil moisture sensor reuse, and where does it normally live?",
        {"soil-moisture-project.md", "electronics-bench.md"},
    ),
    (
        "What tool did Priya borrow to fix her lamp, and who else regularly uses that tool?",
        {"book-club.md", "electronics-bench.md"},
    ),
    (
        "Where is the multimeter kept, and who used it on the greenhouse's humidity sensor?",
        {"electronics-bench.md", "maintenance-log.md"},
    ),
]


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


def build_chunk_store(notes_dir: Path) -> list[dict]:
    paths = sorted(notes_dir.glob("*.md"))
    texts = [p.read_text() for p in paths]
    vectors = embed_texts(texts)
    return [{"source": p.name, "embedding": v} for p, v in zip(paths, vectors)]


def retrieve_chunks(query_vector: list[float], store: list[dict], k: int) -> list[dict]:
    ranked = sorted(
        store, key=lambda item: cosine_similarity(query_vector, item["embedding"]), reverse=True
    )
    return ranked[:k]


def find_starting_node(query_vector: list[float], graph: Graph, node_vectors: dict) -> str:
    node_names = list(graph.keys())
    scores = [cosine_similarity(query_vector, node_vectors[name]) for name in node_names]
    best_index = max(range(len(node_names)), key=lambda i: scores[i])
    return node_names[best_index]


def gather_facts_and_nodes(graph: Graph, start: str, max_hops: int) -> set[str]:
    frontier = {start}
    visited = {start}
    for _ in range(max_hops):
        next_frontier = set()
        for node in frontier:
            for _relation, other in graph.get(node, []):
                if other not in visited:
                    next_frontier.add(other)
                    visited.add(other)
        frontier = next_frontier
    return visited


def precision_at_k_chunks(
    questions: list[tuple[str, set[str]]], store: list[dict], query_vectors: list[list[float]], k: int
) -> float:
    hits = 0
    print(f"Chunk-based precision@{k} (naive retrieval):")
    for (query, needed_sources), query_vector in zip(questions, query_vectors):
        retrieved = retrieve_chunks(query_vector, store, k)
        retrieved_sources = {r["source"] for r in retrieved}
        hit = needed_sources.issubset(retrieved_sources)
        hits += hit
        tag = "HIT " if hit else "MISS"
        print(f"  [{tag}] {query!r} -> needed {needed_sources}, got {retrieved_sources}")
    score = hits / len(questions)
    print(f"  Score: {score:.2f} ({hits}/{len(questions)})\n")
    return score


def precision_at_k_graph(
    questions: list[tuple[str, set[str]]],
    graph: Graph,
    provenance: Provenance,
    node_vectors: dict,
    query_vectors: list[list[float]],
    max_hops: int,
) -> float:
    hits = 0
    print(f"Graph-based precision@{max_hops} hops (traversal):")
    for (query, needed_sources), query_vector in zip(questions, query_vectors):
        start = find_starting_node(query_vector, graph, node_vectors)
        touched_nodes = gather_facts_and_nodes(graph, start, max_hops)
        covered_sources: set[str] = set()
        for node in touched_nodes:
            covered_sources |= provenance.get(node, set())
        hit = needed_sources.issubset(covered_sources)
        hits += hit
        tag = "HIT " if hit else "MISS"
        print(f"  [{tag}] {query!r} -> needed {needed_sources}, covered {covered_sources}")
    score = hits / len(questions)
    print(f"  Score: {score:.2f} ({hits}/{len(questions)})\n")
    return score


def main() -> None:
    graph, provenance = build_graph_with_provenance(NOTES_DIR)
    store = build_chunk_store(NOTES_DIR)

    questions_text = [q for q, _ in LABELED_QUESTIONS]
    query_vectors = embed_texts(questions_text)

    node_names = list(graph.keys())
    node_vector_list = embed_texts(node_names)
    node_vectors = dict(zip(node_names, node_vector_list))

    chunk_score = precision_at_k_chunks(LABELED_QUESTIONS, store, query_vectors, k=2)
    graph_score = precision_at_k_graph(
        LABELED_QUESTIONS, graph, provenance, node_vectors, query_vectors, max_hops=2
    )

    print(f"Summary: chunk-based={chunk_score:.2f}, graph-based={graph_score:.2f}")


if __name__ == "__main__":
    main()
