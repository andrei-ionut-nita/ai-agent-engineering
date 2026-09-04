"""
Lesson 12: instead of a separate classify-then-dispatch step, let the
model choose the retrieval strategy itself, as a Gemini native function
call.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/02_intermediate/12_agentic_tool_based_routing/lesson.py
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

# One tool per strategy. Beginner Lessons 3-6 asked the model "what
# label is this question," a separate step, then this course's own code
# looked the label up in a routing table. Here there is no label and no
# lookup table: the model is handed three tools by name and description
# and asked to pick one directly, the strategy choice and the "answer
# this" step collapse into a single decision.
USE_NAIVE_DECLARATION = types.FunctionDeclaration(
    name="use_naive_retrieval",
    description=(
        "Use for a specific factual lookup answerable from a single "
        "passage in ONE document (a number, a setting, a schedule)."
    ),
)
USE_MULTI_HOP_DECLARATION = types.FunctionDeclaration(
    name="use_multi_hop_retrieval",
    description=(
        "Use when answering the question requires combining facts that "
        "live in TWO DIFFERENT documents."
    ),
)
USE_CORRECTIVE_DECLARATION = types.FunctionDeclaration(
    name="use_corrective_retrieval",
    description=(
        "Use when the question is vague, underspecified, or its scope "
        "could span more than one unrelated document, so the first "
        "retrieved passage should be graded before it's trusted."
    ),
)

ROUTING_TOOL = types.Tool(
    function_declarations=[
        USE_NAIVE_DECLARATION,
        USE_MULTI_HOP_DECLARATION,
        USE_CORRECTIVE_DECLARATION,
    ]
)


# The free tier's requests-per-minute limit is easy to hit once a run
# makes several embed and generate calls back to back. A short backoff-
# and-retry on a 429 keeps this lesson runnable without asking you to
# slow down by hand.
def call_model(**kwargs) -> "types.GenerateContentResponse":
    for attempt in range(5):
        try:
            return client.models.generate_content(**kwargs)
        except ClientError as error:
            if error.code == 429 and attempt < 4:
                time.sleep(15)
                continue
            raise
    raise RuntimeError("Exceeded retries calling the model")


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


def grade_chunk(question: str, chunk_text: str) -> str:
    prompt = (
        "You are grading whether a retrieved passage is relevant enough "
        "to help answer a question. Respond with exactly one word: "
        '"relevant" or "not_relevant".\n\n'
        f"Question: {question}\n\nPassage:\n{chunk_text}"
    )
    response = call_model(model=CHAT_MODEL, contents=prompt)
    grade = (response.text or "").strip().lower()
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


STRATEGIES = {
    "use_naive_retrieval": lambda q, store: retrieve(q, store, k=1),
    "use_multi_hop_retrieval": lambda q, store: retrieve(q, store, k=2),
}


def use_corrective_retrieval(question: str, store: list[dict]) -> list[dict]:
    top1 = retrieve(question, store, k=1)
    if grade_chunk(question, top1[0]["text"]) == "relevant":
        return top1
    return retrieve(question, store, k=2)


STRATEGIES["use_corrective_retrieval"] = use_corrective_retrieval


def agentic_route(question: str, store: list[dict]) -> dict:
    prompt = (
        "Choose the right retrieval tool for this question over a small "
        "personal notes collection (a weather station, a garden, a pizza "
        f"dough recipe, a bookshelf, and cello practice).\n\nQuestion: {question}"
    )
    response = call_model(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(tools=[ROUTING_TOOL], temperature=0),
    )
    calls = response.function_calls
    if not calls:
        # Gemini can always choose to answer directly instead of calling
        # a tool; this course routes so every question below is written
        # to make a tool call unambiguously the right move, but the code
        # itself doesn't assume that, it falls back to the naive tool.
        tool_name = "use_naive_retrieval"
    else:
        tool_name = calls[0].name

    retrieved = STRATEGIES[tool_name](question, store)
    return {"question": question, "tool_chosen": tool_name, "sources": [r["source"] for r in retrieved]}


def main() -> None:
    store = build_vector_store()

    questions = [
        "What oven setting does the pizza dough recipe use?",
        "What two hobbies happen in the same room as the weather station?",
        "How does wind speed affect things around the house?",
    ]

    for question in questions:
        result = agentic_route(question, store)
        print(f"Q: {result['question']}")
        print(f"  tool chosen: {result['tool_chosen']}")
        print(f"  sources retrieved: {result['sources']}\n")

    print(
        "Beginner Lessons 3-6 spent one call classifying (\"what label is "
        "this?\") and then this course's own dispatch code looked that "
        "label up in a routing table to decide what to run. Here, the "
        "model is handed the strategies directly as tools and picks one "
        "itself, in the same call, no separate label and no lookup table "
        "in between. The tradeoff: with a classifier, the routing logic "
        "lives in your own readable if/elif code; with tool-based "
        "routing, it lives inside the model's judgment call, harder to "
        "inspect, but one call instead of two, and no routing table to "
        "keep in sync with the strategies it points to."
    )


if __name__ == "__main__":
    main()
