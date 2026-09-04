"""
Lesson 21: wiring in the real Advanced-tier implementations from
naive_rag, hybrid_rag, graph_rag, corrective_rag, and agentic_rag,
composing five already-conforming Strategy implementations instead of
reconciling five bespoke ones.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/03_advanced/21_wiring_in_the_real_series_strategies/lesson.py
"""

import importlib.util
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType

import chromadb

REPO_ROOT = Path(__file__).resolve().parents[4]
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


def _load_lesson_module(name: str, relative_path: str) -> ModuleType:
    # Every course's Lesson 23 lives in a folder that starts with a
    # digit ("23_refactoring_into..."), which can't be named in a normal
    # `import` statement (Python identifiers can't start with a digit).
    # importlib.util.spec_from_file_location sidesteps that entirely: it
    # loads a module straight from a file path, no package or importable
    # name required, the standard workaround for exactly this situation.
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
hybrid = _load_lesson_module(
    "hybrid_lesson23", "lessons/hybrid_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py"
)
graph = _load_lesson_module(
    "graph_lesson23", "lessons/graph_rag/03_advanced/23_refactoring_into_ingest_and_ask/lesson.py"
)
corrective = _load_lesson_module(
    "corrective_lesson23",
    "lessons/corrective_rag/03_advanced/23_refactoring_into_ingest_grade_correct_ask/lesson.py",
)
agentic = _load_lesson_module(
    "agentic_lesson23", "lessons/agentic_rag/03_advanced/23_refactoring_into_tools_and_run_agent/lesson.py"
)

# Every course above already implements this series' shared Strategy
# protocol (docs/RAG-SERIES-PLAN/README.md): ingest(...) -> State,
# ask(query, state, k) -> str. What differs, course to course, is only
# the exact shape of ingest()'s input, not the protocol's two-function
# boundary:
#   - naive_rag and agentic_rag build their own chromadb collection
#     from a caller-supplied chroma_client, so ingest() takes
#     (notes_dir, chroma_client) instead of notes_dir alone.
#   - graph_rag's ingest() takes docs as a list[Path] rather than a
#     directory, since it iterates documents one at a time to extract
#     relationships.
#   - hybrid_rag and corrective_rag build their own chromadb.Client()
#     internally, so ingest() takes notes_dir alone.
# These are call-site argument shapes, not a break in the protocol
# itself (every ask() still takes (query, state, k) and returns a
# string). Adapting to each shape here, once, is what "composing five
# conforming implementations" means in practice: this lesson never
# reimplements retrieval, grading, traversal, or tool dispatch, it only
# calls each course's real ingest() with the argument shape that
# course's own Lesson 23 already defined.


# chromadb's default in-memory client is a shared, process-wide store
# (chromadb.Client() with default settings resolves to the same
# underlying System every time it's called, not a fresh one per call),
# and four of these five courses' Lesson 23 all name their collection
# "notes". Ingesting all five in one process, one after another, would
# otherwise have each later ingest() either collide with or silently
# replace the "notes" collection an earlier one just built, corrupting
# an already-ingested strategy's state out from under it. This has
# nothing to do with any of the five courses' own code, every one of
# them is correct and already verified in isolation inside its own
# course; it's only a wrinkle from running all five back to back in a
# single process for this lesson's demo. Giving naive_rag and
# agentic_rag (which accept a chroma_client argument) their own
# PersistentClient pointed at a fresh temp directory, and briefly
# patching chromadb.Client for hybrid_rag and corrective_rag (which
# build their own client internally, with no way to inject one from
# outside), isolates each strategy's storage completely, scoped
# entirely to this lesson.


@contextmanager
def _isolated_chroma_client():
    original_client = chromadb.Client
    isolated = chromadb.PersistentClient(path=tempfile.mkdtemp())
    chromadb.Client = lambda *args, **kwargs: isolated  # type: ignore[assignment]
    try:
        yield isolated
    finally:
        chromadb.Client = original_client  # type: ignore[assignment]


def ingest_naive() -> object:
    return naive.ingest(NOTES_DIR, chromadb.PersistentClient(path=tempfile.mkdtemp()))


def ingest_hybrid() -> object:
    with _isolated_chroma_client():
        return hybrid.ingest(NOTES_DIR)


def ingest_graph() -> object:
    # graph_rag's collection is uniquely named ("graph_nodes"), so it
    # never collides with the other four courses' "notes" collection;
    # no isolation needed here.
    return graph.ingest(sorted(NOTES_DIR.glob("*.md")))


def ingest_corrective() -> object:
    with _isolated_chroma_client():
        return corrective.ingest(NOTES_DIR)


def ingest_agentic() -> object:
    return agentic.ingest(NOTES_DIR, chromadb.PersistentClient(path=tempfile.mkdtemp()))


STRATEGIES = {
    "naive": (ingest_naive, naive.ask),
    "hybrid": (ingest_hybrid, hybrid.ask),
    "graph": (ingest_graph, graph.ask),
    "corrective": (ingest_corrective, corrective.ask),
    "agentic": (ingest_agentic, agentic.ask),
}


def main() -> None:
    print("Ingesting this course's fixtures through all five real Advanced-tier strategies...\n")
    states = {}
    for name, (ingest_fn, _) in STRATEGIES.items():
        states[name] = ingest_fn()
        print(f"  {name}: ingested")
    print()

    demo_question = "What two hobbies happen in the same room as the weather station?"
    print(f"Same question, asked through all five real implementations:\nQ: {demo_question}\n")
    for name, (_, ask_fn) in STRATEGIES.items():
        state = states[name]
        answer = ask_fn(demo_question, state, k=2)
        print(f"[{name}] {answer}\n")


if __name__ == "__main__":
    main()
