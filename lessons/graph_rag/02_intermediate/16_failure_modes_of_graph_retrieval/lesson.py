"""
Lesson 16: this course's pedagogical centerpiece. Demonstrates, live,
Graph RAG's central hard problem, error compounding across hops, a
wrong or missing triple at one hop silently corrupting every answer
that depends on reaching a later hop through it. Also demonstrates the
simpler failure of traversal stopping one hop short.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/02_intermediate/16_failure_modes_of_graph_retrieval/lesson.py
"""

import json
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

QUESTION = (
    "Who recalibrated the sensor that Dev flagged as drifting in the "
    "greenhouse, and what tool did they use?"
)
START_ENTITY = "humidity sensor"

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


def corrupt_graph(graph: Graph) -> Graph:
    # Simulate a real extraction failure: silently drop the edge
    # recording that Dev flagged the humidity sensor, the kind of miss
    # that happens on real documents when a sentence's subject is
    # implied by context rather than stated outright. Everything else
    # in the graph is left untouched.
    corrupted = {node: list(edges) for node, edges in graph.items()}
    corrupted["humidity sensor"] = [
        (relation, other)
        for relation, other in corrupted.get("humidity sensor", [])
        if not ("Dev" in other and "flag" in relation.lower())
    ]
    corrupted["Dev"] = [
        (relation, other)
        for relation, other in corrupted.get("Dev", [])
        if "flag" not in relation.lower()
    ]
    return corrupted


def gather_facts(graph: Graph, start: str, max_hops: int) -> list[str]:
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
other usually describe the same underlying event.

Before answering, scan the ENTIRE list below line by line, it is short
enough to check exhaustively. Combine every fact that bears on the
question into a single coherent answer. Only say a detail "isn't
supported" after you have actually checked every fact and confirmed
none of them mention it, don't say a detail is missing if it appears
literally in the list.

Facts:
{context}

Question: {query}"""
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0),
    )
    return response.text or ""


def main() -> None:
    graph = build_graph(NOTES_DIR)

    print("--- Demonstration 1: a wrong/missing extraction at hop 1 ---\n")

    correct_facts = gather_facts(graph, START_ENTITY, max_hops=2)
    print("Answer (correct graph):")
    print(generate_answer(QUESTION, correct_facts))
    print()

    corrupted = corrupt_graph(graph)
    corrupted_facts = gather_facts(corrupted, START_ENTITY, max_hops=2)
    print("Answer (corrupted graph, Dev's flag silently removed):")
    print(generate_answer(QUESTION, corrupted_facts))
    print()

    print("--- Demonstration 2: traversal that stops one hop short ---\n")
    for depth in (1, 2):
        facts = gather_facts(graph, START_ENTITY, max_hops=depth)
        answer = generate_answer(QUESTION, facts)
        print(f"depth={depth}: {answer}\n")


if __name__ == "__main__":
    main()
