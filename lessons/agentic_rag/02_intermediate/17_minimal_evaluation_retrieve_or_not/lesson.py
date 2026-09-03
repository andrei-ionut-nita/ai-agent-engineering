"""
Lesson 17: scoring how often the agent correctly decides whether to
retrieve, against a small, hand-labeled question set.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/02_intermediate/17_minimal_evaluation_retrieve_or_not/lesson.py
"""

import math
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"
MAX_STEPS = 4

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

# The "labeled" part of a labeled evaluation set: for each question, a
# human (you, reading the fixtures) has already decided whether
# retrieval is actually needed to answer it correctly.
LABELED_QUESTIONS = [
    ("How often does the sourdough starter need feeding at room temperature?", True),
    ("How is the vinyl collection organized on the shelves?", True),
    ("What's the signal chain order on the guitar pedalboard?", True),
    ("What is the chemical symbol for gold?", False),
    ("What's the capital of Japan?", False),
    ("What's 12 times 12?", False),
]


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
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


def search_notes(query: str, store: list[dict], k: int = 1) -> str:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    top_k = scored[:k]
    return "\n\n---\n\n".join(f"[{r['source']}]\n{r['text']}" for r in top_k)


SEARCH_NOTES_DECLARATION = types.FunctionDeclaration(
    name="search_notes",
    description=(
        "Search a personal notes collection (sourdough starter, home "
        "aquarium, vinyl collection, guitar pedalboard, and a Japanese "
        "study journal) for passages relevant to a query. Use this only "
        "for questions about these specific personal topics, not for "
        "general knowledge questions."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"query": types.Schema(type=types.Type.STRING, description="What to search for.")},
        required=["query"],
    ),
)

TOOLS = types.Tool(function_declarations=[SEARCH_NOTES_DECLARATION])
CONFIG = types.GenerateContentConfig(tools=[TOOLS])


def ask(query: str, store: list[dict]) -> tuple[str, bool]:
    # Returns (answer, did_retrieve) so evaluation can compare the
    # decision, not just the final answer text.
    contents: list[types.Content] = [types.Content(role="user", parts=[types.Part(text=query)])]

    for _ in range(MAX_STEPS):
        response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=CONFIG)
        calls = response.function_calls
        if not calls:
            return response.text or "", contents_have_tool_call(contents)

        call = calls[0]
        result = search_notes(call.args["query"], store)
        assert response.candidates is not None
        contents.append(response.candidates[0].content)
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_function_response(name=call.name, response={"result": result})],
            )
        )

    return "I wasn't able to fully answer this within the allowed number of search steps.", True


def contents_have_tool_call(contents: list[types.Content]) -> bool:
    return any(
        part.function_call is not None for content in contents for part in (content.parts or [])
    )


def evaluate(store: list[dict]) -> float:
    correct = 0
    for question, should_retrieve in LABELED_QUESTIONS:
        _, did_retrieve = ask(question, store)
        hit = did_retrieve == should_retrieve
        correct += hit
        print(
            f"  [{'HIT ' if hit else 'MISS'}] {question!r} "
            f"-> expected retrieve={should_retrieve}, got retrieve={did_retrieve}"
        )
    return correct / len(LABELED_QUESTIONS)


def main() -> None:
    store = build_vector_store()
    print("Retrieve-or-not evaluation:")
    score = evaluate(store)
    print(f"\n  Accuracy: {score:.2f} ({int(score * len(LABELED_QUESTIONS))}/{len(LABELED_QUESTIONS)})")


if __name__ == "__main__":
    main()
