"""
Lesson 10: finding a graph traversal's starting entity by embedding
similarity, instead of typing it in by hand.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/02_intermediate/10_combining_graph_and_vector_retrieval/lesson.py
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

QUESTION = (
    "Who recalibrated the sensor that Dev flagged as drifting in the "
    "greenhouse, and what tool did they use?"
)

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


def find_starting_node(query: str, graph: Graph) -> str:
    node_names = list(graph.keys())
    node_vectors = embed_texts(node_names)
    query_vector = embed_texts([query])[0]
    scores = [cosine_similarity(query_vector, v) for v in node_vectors]
    best_index = max(range(len(node_names)), key=lambda i: scores[i])
    return node_names[best_index]


def gather_facts(graph: Graph, start: str, max_hops: int = 2) -> list[str]:
    facts = []
    frontier = {start}
    visited = {start}
    for _ in range(max_hops):
        next_frontier = set()
        for node in frontier:
            for relation, other in graph.get(node, []):
                facts.append(f"{node} {relation} {other}")
                if other not in visited:
                    next_frontier.add(other)
                    visited.add(other)
        frontier = next_frontier
    return facts


def generate_answer(query: str, facts: list[str]) -> str:
    context = "\n".join(facts)
    prompt = f"""You are answering a question using facts gathered by
traversing a knowledge graph, not a single passage of prose. The facts
are short (subject, relation, object) statements, listed in the order
traversal found them; facts about the same entity that appear near each
other usually describe the same underlying event. Combine them into a
single coherent answer using only what the facts support. If a specific
detail genuinely isn't supported by any fact, say so plainly instead of
guessing.

Facts:
{context}

Question: {query}"""
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def main() -> None:
    graph = build_graph(NOTES_DIR)

    print(f"Question: {QUESTION}\n")

    best_node = find_starting_node(QUESTION, graph)
    print(f"Best-matching starting node (by embedding similarity): {best_node!r}\n")

    # A vector-picked starting node is often one hop further from the
    # answer than a hand-picked one (Lesson 7 started right at "humidity
    # sensor"; embedding similarity here lands on "greenhouse" instead,
    # a real but less precise match), so this traverses one hop deeper
    # to compensate. Lesson 14 covers the tradeoff that creates.
    facts = gather_facts(graph, best_node, max_hops=3)
    answer = generate_answer(QUESTION, facts)
    print(f"Answer:\n{answer}")


if __name__ == "__main__":
    main()
