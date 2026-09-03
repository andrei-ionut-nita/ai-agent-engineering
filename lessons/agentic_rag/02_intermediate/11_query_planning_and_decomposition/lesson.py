"""
Lesson 11: steering the model to explicitly decompose a compound
question into separate sub-queries, one search_notes() call per part,
instead of relying on it to figure that out unprompted.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/02_intermediate/11_query_planning_and_decomposition/lesson.py
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

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

SYSTEM_INSTRUCTION = """You answer questions using a search_notes tool that
searches one source document at a time. If a question has more than one
distinct part, or asks about more than one topic, call search_notes
once per part, with a separate, focused query for each part, rather
than one broad query covering everything. Only combine your findings
into a single answer once you've gathered a result for every part of
the question."""


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
        "Search a personal notes collection for passages relevant to a "
        "query. Returns passages from ONE source document at a time."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(
                type=types.Type.STRING,
                description="A single, focused search topic, not a compound question.",
            ),
        },
        required=["query"],
    ),
)

TOOLS = types.Tool(function_declarations=[SEARCH_NOTES_DECLARATION])
CONFIG = types.GenerateContentConfig(tools=[TOOLS], system_instruction=SYSTEM_INSTRUCTION)


def ask(query: str, store: list[dict]) -> tuple[str, list[str]]:
    # Same loop shape as Lesson 10, now also collecting every query the
    # model chose to search for, so main() can show the decomposition
    # happening, not just its end result.
    contents: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=query)])
    ]
    sub_queries: list[str] = []

    while True:
        response = client.models.generate_content(
            model=CHAT_MODEL, contents=contents, config=CONFIG
        )
        calls = response.function_calls
        if not calls:
            return response.text or "", sub_queries

        call = calls[0]
        sub_query = call.args["query"]
        sub_queries.append(sub_query)
        result = search_notes(sub_query, store)

        assert response.candidates is not None
        contents.append(response.candidates[0].content)
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_function_response(name=call.name, response={"result": result})],
            )
        )


def main() -> None:
    store = build_vector_store()
    question = (
        "What's the recommended cable-checking interval for the guitar "
        "pedalboard, and how far along is the Japanese study journal "
        "toward the JLPT N3 exam?"
    )

    print(f"Compound question: {question}\n")
    answer, sub_queries = ask(question, store)

    print("Sub-queries the model chose to search for, in order:")
    for i, sub_query in enumerate(sub_queries, start=1):
        print(f"  {i}. {sub_query!r}")

    print(f"\nA: {answer}")


if __name__ == "__main__":
    main()
