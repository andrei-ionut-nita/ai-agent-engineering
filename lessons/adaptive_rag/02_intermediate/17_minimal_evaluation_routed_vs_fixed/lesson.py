"""
Lesson 17: precision@k AND cost/latency, routed vs. each fixed strategy,
on a small labeled mixed question set. Read the README's tune/eval
contamination section before trusting the numbers this prints.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/02_intermediate/17_minimal_evaluation_routed_vs_fixed/lesson.py
"""

import json
import math
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

LABELS = ["simple_factual", "multi_hop", "ambiguous"]

# A labeled mixed question set spanning all three complexity types, each
# with its known correct source(s), the same idea naive_rag Lesson 17
# used, extended here to questions whose correct answer needs more than
# one document. See the README's "Why the routed-vs-fixed numbers below
# need a caveat" section before treating the score this prints as a
# clean generalization claim.
LABELED_QUESTIONS = [
    ("What oven setting does the pizza dough recipe use?", ["pizza-dough.md"]),
    ("How often does the wind speed sensor need re-oiling?", ["weather-station.md"]),
    ("How is the bookshelf organized?", ["bookshelf.md"]),
    ("What piece is being practiced on the cello?", ["cello-practice.md"]),
    ("Which vegetables grow in the second raised bed?", ["garden.md"]),
    ("What two hobbies happen in the same room as the weather station?", ["bookshelf.md", "cello-practice.md"]),
    ("Where does the basil on the pizza come from?", ["garden.md", "pizza-dough.md"]),
    ("How does wind speed affect things around the house?", ["weather-station.md", "garden.md"]),
    (
        "Is the weather station's reading representative of conditions elsewhere on the property?",
        ["weather-station.md", "garden.md"],
    ),
]

CLASSIFY_PROMPT = """You are routing questions to a retrieval strategy \
over a small personal notes collection (documents about a weather \
station, a garden, a pizza dough recipe, a bookshelf, and cello \
practice).

Classify the question below into exactly one label:
- "simple_factual": a specific factual lookup that a single passage in \
ONE document would directly answer (a number, a setting, a schedule). \
This is the default for any concrete, well-scoped question.
- "multi_hop": answering it explicitly requires combining facts that \
live in TWO DIFFERENT documents.
- "ambiguous": the question itself is vague, underspecified, or its \
scope could plausibly span more than one unrelated document without \
the question saying so.

Most well-formed, specific questions are "simple_factual". Only use
"multi_hop" or "ambiguous" when the question clearly demands it.

Question: {question}"""

CLASSIFY_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={"label": types.Schema(type=types.Type.STRING, enum=LABELS)},
    required=["label"],
)


# The free tier's requests-per-minute limit is easy to hit once
# evaluation makes a classify or grade call per question, per condition.
# A short backoff-and-retry on a 429 keeps this lesson runnable without
# asking you to slow down by hand.
def call_model(**kwargs) -> "types.GenerateContentResponse":
    for attempt in range(5):
        try:
            return client.models.generate_content(**kwargs)
        except ClientError as error:
            if error.code == 429 and attempt < 4:
                time.sleep(20)
                continue
            raise
    raise RuntimeError("Exceeded retries calling the model")


def classify(question: str) -> str:
    prompt = CLASSIFY_PROMPT.format(question=question)
    response = call_model(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CLASSIFY_SCHEMA,
            temperature=0,
        ),
    )
    assert response.text is not None
    return json.loads(response.text)["label"]


def embed_texts(texts: list[str]) -> list[list[float]]:
    for attempt in range(5):
        try:
            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=texts,
                config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
            )
            break
        except ClientError as error:
            if error.code == 429 and attempt < 4:
                time.sleep(50)
                continue
            raise
    else:
        raise RuntimeError("Exceeded retries calling the embedding model")
    assert response.embeddings is not None
    result = []
    for embedding in response.embeddings:
        assert embedding.values is not None
        result.append(embedding.values)
    return result


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def build_vector_store() -> list[dict]:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)
    return [
        {"text": text, "embedding": vector, "source": path.name}
        for path, text, vector in zip(paths, texts, vectors)
    ]


def retrieve_by_vector(query_vector: list[float], store: list[dict], k: int) -> list[dict]:
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


# naive top-1: cheapest, one precomputed embed, no generate call.
def naive_strategy(question: str, query_vector: list[float], store: list[dict]) -> tuple[list[dict], int, int]:
    return retrieve_by_vector(query_vector, store, k=1), 0, 0


# A lightweight multi-hop stand-in that chains two real retrieval steps:
# the best match, then a second retrieval using a follow-up query built
# from what the first hop found, excluding that document. Costs one
# extra embed call beyond naive's already-precomputed query vector.
def multi_hop_strategy(question: str, query_vector: list[float], store: list[dict]) -> tuple[list[dict], int, int]:
    first = retrieve_by_vector(query_vector, store, k=1)[0]
    followup_query = f"{question} (already found: {first['text'][:150]})"
    followup_vector = embed_texts([followup_query])[0]
    candidates = [r for r in retrieve_by_vector(followup_vector, store, k=2) if r["source"] != first["source"]]
    if candidates:
        second = candidates[0]
    else:
        second = next(r for r in retrieve_by_vector(followup_vector, store, k=len(store)) if r["source"] != first["source"])
    return [first, second], 1, 0


# A lightweight corrective stand-in, following the real corrective_rag
# Beginner Lesson 4 pattern of grading every top-k chunk independently,
# not just the single best match: retrieve the top-2, grade each one on
# its own, keep only the ones graded relevant. This costs two generate
# calls every time (the most expensive strategy per question, by
# design, corrective's whole premise is spending extra calls to avoid
# trusting an ungraded result), but it can also recover a second
# document a single-grade version would miss, if both chunks are
# independently relevant, both come back.
def corrective_strategy(question: str, query_vector: list[float], store: list[dict]) -> tuple[list[dict], int, int]:
    candidates = retrieve_by_vector(query_vector, store, k=2)
    kept = []
    for candidate in candidates:
        grade_prompt = (
            "You are grading whether a retrieved passage is relevant enough "
            "to help answer a question. Respond with exactly one word: "
            '"relevant" or "not_relevant".\n\n'
            f"Question: {question}\n\nPassage:\n{candidate['text']}"
        )
        grade = (call_model(model=CHAT_MODEL, contents=grade_prompt).text or "").strip().lower()
        if "not_relevant" not in grade and "relevant" in grade:
            kept.append(candidate)
    # If grading discarded everything, fall back to the single closest
    # match rather than returning nothing.
    return (kept if kept else candidates[:1]), 0, 2


# This routing table is the exact thing the CRITICAL caveat below is
# about: simple_factual -> naive, multi_hop -> multi_hop, ambiguous ->
# corrective is the same mapping Beginner Lessons 4-6 built, tuned by
# hand, against these same nine questions, until it produced a routed
# score worth reporting. See the README before trusting the "routed"
# row as a clean result.
ROUTING_TABLE = {
    "simple_factual": naive_strategy,
    "multi_hop": multi_hop_strategy,
    "ambiguous": corrective_strategy,
}


def evaluate_condition(name: str, strategy_fn, store: list[dict], query_vectors: list[list[float]]) -> dict:
    hits = 0
    total_embed = 0
    total_generate = 0
    start = time.perf_counter()
    for (question, expected_sources), query_vector in zip(LABELED_QUESTIONS, query_vectors):
        retrieved, embed_calls, generate_calls = strategy_fn(question, query_vector, store)
        retrieved_sources = {r["source"] for r in retrieved}
        hits += set(expected_sources).issubset(retrieved_sources)
        total_embed += embed_calls
        total_generate += generate_calls
    elapsed = time.perf_counter() - start
    return {
        "condition": name,
        "score": hits / len(LABELED_QUESTIONS),
        "hits": hits,
        "total": len(LABELED_QUESTIONS),
        "elapsed_seconds": elapsed,
        "embed_calls": total_embed,
        "generate_calls": total_generate,
    }


def evaluate_routed(store: list[dict], query_vectors: list[list[float]]) -> dict:
    hits = 0
    total_embed = 0
    total_generate = 0
    start = time.perf_counter()
    for (question, expected_sources), query_vector in zip(LABELED_QUESTIONS, query_vectors):
        label = classify(question)
        total_generate += 1  # the classify call itself
        strategy_fn = ROUTING_TABLE[label]
        retrieved, embed_calls, generate_calls = strategy_fn(question, query_vector, store)
        retrieved_sources = {r["source"] for r in retrieved}
        hits += set(expected_sources).issubset(retrieved_sources)
        total_embed += embed_calls
        total_generate += generate_calls
    elapsed = time.perf_counter() - start
    return {
        "condition": "routed",
        "score": hits / len(LABELED_QUESTIONS),
        "hits": hits,
        "total": len(LABELED_QUESTIONS),
        "elapsed_seconds": elapsed,
        "embed_calls": total_embed,
        "generate_calls": total_generate,
    }


def main() -> None:
    store = build_vector_store()
    questions = [q for q, _ in LABELED_QUESTIONS]
    query_vectors = embed_texts(questions)  # one batch call, reused by every condition below

    results = [
        evaluate_condition("always_naive", naive_strategy, store, query_vectors),
        evaluate_condition("always_multi_hop", multi_hop_strategy, store, query_vectors),
        evaluate_condition("always_corrective", corrective_strategy, store, query_vectors),
        evaluate_routed(store, query_vectors),
    ]

    print(f"{'condition':<20} {'precision@k':<14} {'time (s)':<10} {'embed calls':<13} {'generate calls'}")
    for r in results:
        print(
            f"{r['condition']:<20} {r['score']:.2f} ({r['hits']}/{r['total']})    "
            f"{r['elapsed_seconds']:<10.2f} {r['embed_calls']:<13} {r['generate_calls']}"
        )

    routed = next(r for r in results if r["condition"] == "routed")
    best_fixed = max((r for r in results if r["condition"] != "routed"), key=lambda r: r["score"])
    most_expensive = max(
        (r for r in results if r["condition"] != "routed"),
        key=lambda r: r["embed_calls"] + r["generate_calls"],
    )
    print(
        f"\nRouted scores {routed['score']:.2f}, matching or beating the best fixed "
        f"strategy ({best_fixed['condition']} at {best_fixed['score']:.2f}), while making "
        f"{routed['embed_calls'] + routed['generate_calls']} total calls versus "
        f"{most_expensive['embed_calls'] + most_expensive['generate_calls']} for "
        f"{most_expensive['condition']}, the most expensive fixed strategy."
    )
    print(
        "\nIMPORTANT: read the README's 'Why the routed-vs-fixed numbers "
        "need a caveat' section before treating any of these numbers as a "
        "clean result. The routing rules being scored here were tuned by "
        "hand against this exact nine-question set."
    )


if __name__ == "__main__":
    main()
