"""
Lesson 14: measuring how traversal depth trades recall for precision,
combinatorially, and choosing a depth by observing that tradeoff
directly, not by tuning against a labeled evaluation set.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/02_intermediate/14_limiting_traversal_depth/lesson.py
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

START_ENTITY = "humidity sensor"
RELEVANT_TERMS = ["sensor", "Mia", "multimeter", "greenhouse", "recalibrat"]

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


def main() -> None:
    graph = build_graph(NOTES_DIR)

    print(f"Traversal depth vs. gathered facts, starting from {START_ENTITY!r}:\n")
    for depth in (1, 2, 3, 4):
        facts = gather_facts(graph, START_ENTITY, max_hops=depth)
        relevant = sum(
            1 for f in facts if any(term.lower() in f.lower() for term in RELEVANT_TERMS)
        )
        print(f"depth={depth}: {len(facts)} facts gathered, {relevant} plausibly relevant")


if __name__ == "__main__":
    main()
