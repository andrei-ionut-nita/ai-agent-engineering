"""
Lesson 25: Advanced Capstone. A complete Adaptive RAG service combining
all five real strategies from the series behind one /ask endpoint. No
new concepts, this is Lessons 19-24 combined into one thing, with the
registry finally widened from three strategies to all five.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/03_advanced/25_advanced_capstone_project/lesson.py

To run this as a real, live server instead:

    uvicorn lesson:app --reload
"""

import importlib.util
import json
import sys
import tempfile
import time
from contextlib import asynccontextmanager, contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from types import ModuleType
from typing import Callable

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"
REPO_ROOT = Path(__file__).resolve().parents[4]
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

CLASSIFY_PROMPT = """Classify the question below as exactly one of:
simple_factual, keyword_or_id_lookup, multi_hop, ambiguous, needs_computation_or_tool.

simple_factual: answerable from a single fact in a single document, no
  arithmetic or external tool needed.
keyword_or_id_lookup: hinges on a specific term, phrase, or name that
  should be matched close to literally, not just semantically.
multi_hop: requires combining facts from two or more documents.
ambiguous: the question's scope or intent isn't fully clear, or it
  touches more than one topic without a clean single answer.
needs_computation_or_tool: requires arithmetic, a date/time lookup, or
  some other operation a plain retrieval-and-generate pass can't do.

Return ONLY a JSON object like {{"label": "simple_factual", "reason": "<one short phrase>"}}.

Question: {question}"""

# Every strategy this series built gets exactly one route, matching the
# specific strength each one demonstrated in its own course (recapped
# in Lesson 2): naive for a clean single-fact lookup, hybrid for a
# keyword/ID-anchored query (hybrid_rag's own Lesson 6 case), graph for
# multi-hop, corrective for an ambiguous, needs-checking question, and
# agentic for anything needing a tool call rather than retrieval alone.
ROUTES: dict[str, str] = {
    "simple_factual": "naive",
    "keyword_or_id_lookup": "hybrid",
    "multi_hop": "graph",
    "ambiguous": "corrective",
    "needs_computation_or_tool": "agentic",
}


def _load_lesson_module(name: str, relative_path: str) -> ModuleType:
    file_path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, file_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


naive = _load_lesson_module(
    "naive_lesson23_cap", "lessons/naive_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py"
)
hybrid = _load_lesson_module(
    "hybrid_lesson23_cap", "lessons/hybrid_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py"
)
graph = _load_lesson_module(
    "graph_lesson23_cap", "lessons/graph_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py"
)
corrective = _load_lesson_module(
    "corrective_lesson23_cap",
    "lessons/corrective_rag/03_advanced/23_refactoring_into_ingest_grade_correct_ask/lesson.py",
)
agentic = _load_lesson_module(
    "agentic_lesson23_cap", "lessons/agentic_rag/03_advanced/23_refactoring_into_tools_and_run_agent/lesson.py"
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
    name: str
    state: object
    ask: Callable[[str, object, int], str]


def build_registry() -> dict[str, Strategy]:
    # Every ingest() call below is the real thing from that course's own
    # Lesson 23, called with the argument shape that course's own
    # Lesson 23 already defined (Lesson 21's finding), each isolated
    # into its own storage so five courses' worth of ingestion can run
    # in one process without one strategy's collection stepping on
    # another's (also Lesson 21).
    naive_state = naive.ingest(NOTES_DIR, chromadb.PersistentClient(path=tempfile.mkdtemp()))
    with _isolated_chroma_client():
        hybrid_state = hybrid.ingest(NOTES_DIR)
    graph_state = graph.ingest(sorted(NOTES_DIR.glob("*.md")))
    with _isolated_chroma_client():
        corrective_state = corrective.ingest(NOTES_DIR)
    agentic_state = agentic.ingest(NOTES_DIR, chromadb.PersistentClient(path=tempfile.mkdtemp()))

    return {
        "naive": Strategy("naive", naive_state, naive.ask),
        "hybrid": Strategy("hybrid", hybrid_state, hybrid.ask),
        "graph": Strategy("graph", graph_state, graph.ask),
        "corrective": Strategy("corrective", corrective_state, corrective.ask),
        "agentic": Strategy("agentic", agentic_state, agentic.ask),
    }


@dataclass
class RoutingLogEntry:
    question: str
    label: str
    reason: str
    strategy: str
    latency_seconds: float


ROUTING_LOG: list[RoutingLogEntry] = []


def classify(query: str) -> tuple[str, str]:
    prompt = CLASSIFY_PROMPT.format(question=query)
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0),
    )
    assert response.text is not None
    parsed = json.loads(response.text)
    return parsed["label"], parsed.get("reason", "")


def route(label: str) -> str:
    return ROUTES.get(label, "naive")


def answer(query: str, registry: dict[str, Strategy], k: int = 2) -> tuple[str, str]:
    start = time.monotonic()
    label, reason = classify(query)
    strategy_name = route(label)
    strategy = registry[strategy_name]
    response_text = strategy.ask(query, strategy.state, k)
    elapsed = time.monotonic() - start

    entry = RoutingLogEntry(
        question=query, label=label, reason=reason, strategy=strategy_name, latency_seconds=round(elapsed, 2)
    )
    ROUTING_LOG.append(entry)

    return strategy_name, response_text


class AskResponse(BaseModel):
    answer: str
    strategy: str
    reason: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.registry = build_registry()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str, k: int = 2) -> AskResponse:
    strategy_name, response_text = answer(q, app.state.registry, k)
    reason = ROUTING_LOG[-1].reason if ROUTING_LOG else ""
    return AskResponse(answer=response_text, strategy=strategy_name, reason=reason)


@app.get("/logs")
def logs_endpoint() -> list[dict]:
    return [asdict(entry) for entry in ROUTING_LOG]


# One demo question per strategy, deliberately, so a single run of this
# capstone provably exercises all five of this series' real
# implementations, not just whichever one the classifier happens to
# favor.
DEMO_QUESTIONS = [
    "What oven setting does the pizza dough recipe use?",
    "What is the windowpane test used for when mixing pizza dough?",
    "What two hobbies happen in the same room as the weather station?",
    "How does wind speed affect things around the house?",
    "The pizza dough's cold ferment takes 48 hours. How many hours is that doubled?",
]


def main() -> None:
    with TestClient(app) as test_client:
        strategies_used = set()
        for question in DEMO_QUESTIONS:
            response = test_client.get("/ask", params={"q": question})
            body = response.json()
            strategies_used.add(body["strategy"])
            print(f"GET /ask?q={question!r}")
            print(f"  {body}\n")

        print(f"Strategies exercised this run: {sorted(strategies_used)}")
        print(f"All five strategies used: {strategies_used == set(ROUTES.values())}")


if __name__ == "__main__":
    main()
