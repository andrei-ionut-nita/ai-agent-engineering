"""
Lesson 22: a clean route() function plus a name-to-strategy registry,
built on top of Lesson 21's five real, wired-in strategies.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/03_advanced/22_a_route_and_strategy_registry_pattern/lesson.py
"""

import importlib.util
import json
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Callable

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"
REPO_ROOT = Path(__file__).resolve().parents[4]
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

CLASSIFY_PROMPT = """Classify the question below as exactly one of:
simple_factual, multi_hop, ambiguous.

simple_factual: answerable from a single fact in a single document.
multi_hop: requires combining facts from two or more documents.
ambiguous: the question's scope or intent isn't fully clear, or it
touches more than one topic without a clean single answer.

Return ONLY a JSON object like {{"label": "simple_factual"}}.

Question: {question}"""


def _load_lesson_module(name: str, relative_path: str) -> ModuleType:
    file_path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, file_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


naive = _load_lesson_module(
    "naive_lesson23", "lessons/naive_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py"
)
graph = _load_lesson_module(
    "graph_lesson23", "lessons/graph_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py"
)
corrective = _load_lesson_module(
    "corrective_lesson23",
    "lessons/corrective_rag/03_advanced/23_refactoring_into_ingest_grade_correct_ask/lesson.py",
)


@contextmanager
def _isolated_chroma_client():
    original_client = chromadb.Client
    isolated = chromadb.PersistentClient(path=tempfile.mkdtemp())
    chromadb.Client = lambda *args, **kwargs: isolated  # type: ignore[assignment]
    try:
        yield isolated
    finally:
        chromadb.Client = original_client  # type: ignore[assignment]


@dataclass
class Strategy:
    # A registry entry: a human-readable name, a ready-built state, and
    # the real ask() this strategy's own course defined. Everything
    # route() needs to dispatch to a strategy by name lives here.
    name: str
    state: object
    ask: Callable[[str, object, int], str]


def build_registry() -> dict[str, Strategy]:
    # ingest() runs once, here, at registry-build time, the same
    # "expensive setup happens once" shape every course's own Lesson 23
    # already established. Three strategies (not all five, Lesson 21
    # already proved all five wire in the same way) keep this lesson's
    # registry small enough to read in one sitting.
    naive_state = naive.ingest(NOTES_DIR, chromadb.PersistentClient(path=tempfile.mkdtemp()))
    with _isolated_chroma_client():
        corrective_state = corrective.ingest(NOTES_DIR)
    graph_state = graph.ingest(sorted(NOTES_DIR.glob("*.md")))

    return {
        "naive": Strategy("naive", naive_state, naive.ask),
        "corrective": Strategy("corrective", corrective_state, corrective.ask),
        "graph": Strategy("graph", graph_state, graph.ask),
    }


# One label maps to exactly one strategy name; this is the entire
# routing table, deliberately a plain dict instead of a chain of
# if/elif statements, so adding a fourth or fifth route later (Lesson
# 25's capstone does) means adding one line here, not a new branch.
ROUTES: dict[str, str] = {
    "simple_factual": "naive",
    "multi_hop": "graph",
    "ambiguous": "corrective",
}


def classify(query: str) -> str:
    prompt = CLASSIFY_PROMPT.format(question=query)
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0),
    )
    assert response.text is not None
    return json.loads(response.text)["label"]


def route(label: str) -> str:
    return ROUTES.get(label, "naive")


def answer(query: str, registry: dict[str, Strategy], k: int = 2) -> tuple[str, str]:
    # classify() -> route() -> registry[name].ask(), the whole pipeline
    # as three composable steps instead of one long function. Returns
    # (strategy_name, answer) so callers can show which route was taken.
    label = classify(query)
    strategy_name = route(label)
    strategy = registry[strategy_name]
    return strategy_name, strategy.ask(query, strategy.state, k)


def main() -> None:
    print("Building the strategy registry (naive, corrective, graph)...\n")
    registry = build_registry()

    questions = [
        "What oven setting does the pizza dough recipe use?",
        "What two hobbies happen in the same room as the weather station?",
        "How does wind speed affect things around the house?",
    ]
    for query in questions:
        strategy_name, response_text = answer(query, registry)
        print(f"Q: {query}")
        print(f"   routed to: {strategy_name}")
        print(f"   A: {response_text}\n")


if __name__ == "__main__":
    main()
