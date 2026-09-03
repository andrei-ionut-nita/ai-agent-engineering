"""
Lesson 15: generating a multi-hop answer that cites, per hop, which
source document each fact traces back to.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/02_intermediate/15_prompting_for_cited_multi_hop_answers/lesson.py
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


def gather_facts_with_sources(
    graph: Graph, provenance: Provenance, start: str, max_hops: int = 2
) -> list[tuple[str, set[str]]]:
    facts: list[tuple[str, set[str]]] = []
    frontier = {start}
    visited = {start}
    for _ in range(max_hops):
        next_frontier = set()
        for node in frontier:
            for relation, other in graph.get(node, []):
                # Prefer a source that mentions both ends of this edge,
                # the strongest possible attribution. Fall back to the
                # union when the edge was created by merging two nodes
                # from different documents (Lesson 11's normalization).
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


def main() -> None:
    graph, provenance = build_graph_with_provenance(NOTES_DIR)

    print(f"Question: {QUESTION}\n")

    facts = gather_facts_with_sources(graph, provenance, START_ENTITY, max_hops=2)
    answer = generate_cited_answer(QUESTION, facts)
    print(f"Answer:\n{answer}")


if __name__ == "__main__":
    main()
