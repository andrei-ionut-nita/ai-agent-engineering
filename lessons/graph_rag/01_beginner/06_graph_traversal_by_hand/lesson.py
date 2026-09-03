"""
Lesson 6: one-hop and two-hop traversal over a hand-rolled graph.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/01_beginner/06_graph_traversal_by_hand/lesson.py
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

SOURCE_FILES = ["greenhouse.md", "maintenance-log.md", "electronics-bench.md"]

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


def build_graph(triples: list[tuple[str, str, str]]) -> Graph:
    graph: Graph = {}
    for subject, relation, obj in triples:
        add_edge(graph, subject, relation, obj)
    return graph


def one_hop(graph: Graph, node: str) -> list[tuple[str, str]]:
    return graph.get(node, [])


def two_hop(graph: Graph, node: str) -> list[tuple[str, str, str, str]]:
    results = []
    for relation1, neighbor in one_hop(graph, node):
        for relation2, neighbor2 in one_hop(graph, neighbor):
            if neighbor2 == node:
                continue  # skip walking straight back to the start
            results.append((relation1, neighbor, relation2, neighbor2))
    return results


def main() -> None:
    all_triples: list[tuple[str, str, str]] = []
    for filename in SOURCE_FILES:
        text = (NOTES_DIR / filename).read_text()
        all_triples.extend(extract_relationships(text))
    graph = build_graph(all_triples)

    start = "multimeter"
    print(f"One-hop from '{start}':")
    for relation, other in one_hop(graph, start):
        print(f"  {relation} -> {other}")
    print()

    print(f"Two-hop from '{start}':")
    for relation1, mid, relation2, end in two_hop(graph, start):
        print(f"  {relation1} -> {mid} -> {relation2} -> {end}")


if __name__ == "__main__":
    main()
