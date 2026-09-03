"""
Lesson 13: saving the extracted graph to disk as JSON, so subsequent
runs load it instead of re-extracting from the fixture notes.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/02_intermediate/13_persisting_the_graph/lesson.py

Run it twice: the first run extracts and saves, the second loads.
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
GRAPH_PATH = Path(__file__).parent / "graph.json"

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


def save_graph(graph: Graph, path: Path) -> None:
    path.write_text(json.dumps(graph, indent=2))


def load_graph(path: Path) -> Graph:
    raw = json.loads(path.read_text())
    # JSON has no tuple type, edges come back as two-element lists.
    # Convert them back to tuples so downstream code can unpack them
    # the same way whether the graph was just built or just loaded.
    return {node: [tuple(edge) for edge in edges] for node, edges in raw.items()}


def main() -> None:
    if GRAPH_PATH.exists():
        graph = load_graph(GRAPH_PATH)
        print("Loaded graph from disk, no extraction needed.")
    else:
        graph = build_graph(NOTES_DIR)
        save_graph(graph, GRAPH_PATH)
        print("Built graph from scratch and saved it.")

    print(f"Graph has {len(graph)} nodes, saved to {GRAPH_PATH.name}.")


if __name__ == "__main__":
    main()
