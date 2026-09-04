"""
Lesson 24: instrumenting the service, logging which strategy handled
each request and why, on top of Lesson 23's FastAPI app.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/03_advanced/24_instrumenting_strategy_choice/lesson.py
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
simple_factual, multi_hop, ambiguous.

simple_factual: answerable from a single fact in a single document.
multi_hop: requires combining facts from two or more documents.
ambiguous: the question's scope or intent isn't fully clear, or it
touches more than one topic without a clean single answer.

Return ONLY a JSON object like {{"label": "simple_factual", "reason": "<one short phrase>"}}.

Question: {question}"""

ROUTES: dict[str, str] = {
    "simple_factual": "naive",
    "multi_hop": "graph",
    "ambiguous": "corrective",
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
    "naive_lesson23_log", "lessons/naive_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py"
)
graph = _load_lesson_module(
    "graph_lesson23_log", "lessons/graph_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py"
)
corrective = _load_lesson_module(
    "corrective_lesson23_log",
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
    name: str
    state: object
    ask: Callable[[str, object, int], str]


def build_registry() -> dict[str, Strategy]:
    naive_state = naive.ingest(NOTES_DIR, chromadb.PersistentClient(path=tempfile.mkdtemp()))
    with _isolated_chroma_client():
        corrective_state = corrective.ingest(NOTES_DIR)
    graph_state = graph.ingest(sorted(NOTES_DIR.glob("*.md")))

    return {
        "naive": Strategy("naive", naive_state, naive.ask),
        "corrective": Strategy("corrective", corrective_state, corrective.ask),
        "graph": Strategy("graph", graph_state, graph.ask),
    }


@dataclass
class RoutingLogEntry:
    # One record per request: what was asked, what the classifier said
    # and why, which strategy handled it, and how long that took. This
    # is Lesson 13's persisted-decision idea, moved from a script's
    # local list into the service every request now runs through.
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
    print(f"[routing log] {json.dumps(asdict(entry))}")

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


def main() -> None:
    with TestClient(app) as test_client:
        for question in (
            "What oven setting does the pizza dough recipe use?",
            "How does wind speed affect things around the house?",
        ):
            response = test_client.get("/ask", params={"q": question})
            print(f"GET /ask?q={question!r}")
            print(f"  {response.json()}\n")

        print("GET /logs")
        print(f"  {test_client.get('/logs').json()}")


if __name__ == "__main__":
    main()
