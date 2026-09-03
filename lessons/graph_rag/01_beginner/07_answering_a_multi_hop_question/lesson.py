"""
Lesson 7: traverse the graph to gather facts, then generate an answer,
Graph RAG's version of retrieve-then-generate.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/01_beginner/07_answering_a_multi_hop_question/lesson.py
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


def build_graph(triples: list[tuple[str, str, str]]) -> Graph:
    graph: Graph = {}
    for subject, relation, obj in triples:
        add_edge(graph, subject, relation, obj)
    return graph


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
    all_triples: list[tuple[str, str, str]] = []
    for filename in SOURCE_FILES:
        text = (NOTES_DIR / filename).read_text()
        all_triples.extend(extract_relationships(text))
    graph = build_graph(all_triples)

    print(f"Question: {QUESTION}\n")

    facts = gather_facts(graph, START_ENTITY, max_hops=2)
    print(f"Facts gathered by traversal (starting from '{START_ENTITY}'):")
    for fact in facts:
        print(f"  {fact}")
    print()

    answer = generate_answer(QUESTION, facts)
    print(f"Answer:\n{answer}")


if __name__ == "__main__":
    main()
