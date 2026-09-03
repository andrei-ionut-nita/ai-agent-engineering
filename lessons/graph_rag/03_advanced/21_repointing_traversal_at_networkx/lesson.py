"""
Lesson 21: re-pointing extraction and traversal at networkx.DiGraph,
same build_graph/gather_facts interface as Lessons 5-7, a different
backend underneath.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/03_advanced/21_repointing_traversal_at_networkx/lesson.py
"""

import json
from pathlib import Path

import networkx as nx
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


def build_graph(notes_dir: Path) -> nx.DiGraph:
    graph = nx.DiGraph()
    for path in sorted(notes_dir.glob("*.md")):
        for subject, relation, obj in extract_relationships(path.read_text()):
            graph.add_edge(subject, obj, relation=relation)
    return graph


def gather_facts(graph: nx.DiGraph, start: str, max_hops: int = 2) -> list[str]:
    facts: list[str] = []
    frontier = {start}
    visited = {start}
    for _ in range(max_hops):
        next_frontier = set()
        for node in frontier:
            if node not in graph:
                continue
            for _, other, data in graph.out_edges(node, data=True):
                facts.append(f"{node} {data['relation']} {other}")
                if other not in visited:
                    next_frontier.add(other)
                    visited.add(other)
            for other, _, data in graph.in_edges(node, data=True):
                facts.append(f"{other} {data['relation']} {node}")
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
    facts = gather_facts(graph, START_ENTITY, max_hops=2)
    answer = generate_answer(QUESTION, facts)
    print(f"Answer:\n{answer}")


if __name__ == "__main__":
    main()
