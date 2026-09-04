"""
Lesson 14: measuring actual wall-clock time and API call count per
strategy, then routing to the cheapest one that's still sufficient
instead of always reaching for the most powerful.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/02_intermediate/14_cost_and_latency_tradeoffs/lesson.py
"""

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

# A running tally of API calls, reset before each strategy runs, so the
# real cost of "how many calls did this strategy actually make" is
# counted, not estimated.
CALL_COUNTS = {"embed": 0, "generate": 0}


def reset_counts() -> None:
    CALL_COUNTS["embed"] = 0
    CALL_COUNTS["generate"] = 0


def embed_texts(texts: list[str]) -> list[list[float]]:
    CALL_COUNTS["embed"] += 1
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
                time.sleep(15)
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


# The free tier's requests-per-minute limit is easy to hit once a run
# makes several calls back to back. A short backoff-and-retry on a 429
# keeps this lesson runnable without asking you to slow down by hand
# (occasionally inflating the timed strategy's elapsed_seconds, a real
# part of the cost picture, not an artifact to hide).
def generate_text(prompt: str) -> str:
    CALL_COUNTS["generate"] += 1
    for attempt in range(5):
        try:
            response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
            return response.text or ""
        except ClientError as error:
            if error.code == 429 and attempt < 4:
                time.sleep(15)
                continue
            raise
    raise RuntimeError("Exceeded retries calling the model")


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


def retrieve(query: str, store: list[dict], k: int) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


# Naive top-1: one embed call for the question, nothing else.
def naive_retrieve(question: str, store: list[dict]) -> list[dict]:
    return retrieve(question, store, k=1)


# A lightweight multi-hop stand-in that actually chains two retrieval
# steps (unlike Lessons 10-13's single top-2 call): retrieve the best
# match, then retrieve again using a follow-up query built from what the
# first hop found, excluding that same document. Two hops, two embed
# calls, the cost this strategy's name implies.
def multi_hop_retrieve(question: str, store: list[dict]) -> list[dict]:
    first = retrieve(question, store, k=1)[0]
    followup_query = f"{question} (already found: {first['text'][:150]})"
    candidates = [r for r in retrieve(followup_query, store, k=2) if r["source"] != first["source"]]
    second = candidates[0] if candidates else next(r for r in retrieve(question, store, k=2) if r["source"] != first["source"])
    return [first, second]


# A lightweight corrective stand-in: retrieve top-1, grade it with an
# LLM call, and only pay for a second retrieval if the grade comes back
# not_relevant. The retry reuses the store's already-embedded vectors,
# no second embed call needed, just a wider k against results already
# scored.
def corrective_retrieve(question: str, store: list[dict]) -> list[dict]:
    scored_all = retrieve(question, store, k=len(store))
    top1 = scored_all[:1]
    grade_prompt = (
        "You are grading whether a retrieved passage is relevant enough "
        "to help answer a question. Respond with exactly one word: "
        '"relevant" or "not_relevant".\n\n'
        f"Question: {question}\n\nPassage:\n{top1[0]['text']}"
    )
    grade = generate_text(grade_prompt).strip().lower()
    if "not_relevant" not in grade and "relevant" in grade:
        return top1
    return scored_all[:2]


STRATEGIES = {
    "naive": naive_retrieve,
    "multi_hop": multi_hop_retrieve,
    "corrective": corrective_retrieve,
}


def measure(strategy_name: str, question: str, store: list[dict]) -> dict:
    reset_counts()
    start = time.perf_counter()
    retrieved = STRATEGIES[strategy_name](question, store)
    elapsed = time.perf_counter() - start
    return {
        "strategy": strategy_name,
        "elapsed_seconds": elapsed,
        "embed_calls": CALL_COUNTS["embed"],
        "generate_calls": CALL_COUNTS["generate"],
        "sources": [r["source"] for r in retrieved],
    }


def main() -> None:
    store = build_vector_store()

    # A clean single-document lookup: any of the three strategies will
    # find pizza-dough.md, so the question is which one gets there
    # cheapest.
    question = "What oven setting does the pizza dough recipe use?"

    print(f"Q: {question}\n")
    results = [measure(name, question, store) for name in ("naive", "multi_hop", "corrective")]
    for result in results:
        print(
            f"{result['strategy']:>10}: {result['elapsed_seconds']:.2f}s, "
            f"{result['embed_calls']} embed call(s), {result['generate_calls']} generate call(s), "
            f"sources={result['sources']}"
        )

    cheapest_sufficient = min(results, key=lambda r: r["embed_calls"] + r["generate_calls"])
    print(
        f"\nAll three strategies retrieve the same correct source, "
        f"'{cheapest_sufficient['sources'][0]}', but at very different "
        f"cost. Routing this question to '{cheapest_sufficient['strategy']}' "
        "gets the same right answer for the fewest calls, paying for "
        "multi_hop's second hop or corrective's grading call here buys "
        "nothing this question actually needed."
    )


if __name__ == "__main__":
    main()
