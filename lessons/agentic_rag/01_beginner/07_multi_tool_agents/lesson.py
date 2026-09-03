"""
Lesson 7: adding a second, non-retrieval tool alongside search_notes(),
and dispatching to whichever one the model actually asks for.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/01_beginner/07_multi_tool_agents/lesson.py
"""

import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


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


def search_notes(query: str, store: list[dict], k: int = 2) -> str:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    top_k = scored[:k]
    return "\n\n---\n\n".join(f"[{r['source']}]\n{r['text']}" for r in top_k)


def get_current_datetime(timezone: str) -> str:
    # A second tool that has nothing to do with retrieval, deliberately
    # trivial (the standard library's own zoneinfo, no new dependency)
    # so this lesson is about multi-tool dispatch, not about the tool
    # itself.
    try:
        tz = ZoneInfo(timezone)
    except Exception:
        return f"Unknown IANA timezone name: {timezone!r}"
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M %Z")


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
        properties={
            "query": types.Schema(
                type=types.Type.STRING,
                description="What to search for, phrased as a question or topic.",
            ),
        },
        required=["query"],
    ),
)

GET_CURRENT_DATETIME_DECLARATION = types.FunctionDeclaration(
    name="get_current_datetime",
    description="Get the current date and time in a named IANA timezone, e.g. 'Europe/Lisbon' or 'Asia/Tokyo'.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "timezone": types.Schema(
                type=types.Type.STRING,
                description="An IANA timezone name, e.g. 'America/New_York'.",
            ),
        },
        required=["timezone"],
    ),
)

TOOLS = types.Tool(
    function_declarations=[SEARCH_NOTES_DECLARATION, GET_CURRENT_DATETIME_DECLARATION]
)
CONFIG = types.GenerateContentConfig(tools=[TOOLS])


def run_tool(call: types.FunctionCall, store: list[dict]) -> str:
    # A hand-rolled if/elif dispatch, exactly two branches for exactly
    # two tools. This is deliberately the simplest thing that works;
    # Lesson 19 comes back to this same shape once a third and fourth
    # tool make it start to strain.
    if call.name == "search_notes":
        return search_notes(call.args["query"], store)
    elif call.name == "get_current_datetime":
        return get_current_datetime(call.args["timezone"])
    else:
        raise ValueError(f"Unknown tool: {call.name}")


def ask(query: str, store: list[dict]) -> str:
    contents: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=query)])
    ]
    response = client.models.generate_content(
        model=CHAT_MODEL, contents=contents, config=CONFIG
    )

    calls = response.function_calls
    if not calls:
        return response.text or ""

    call = calls[0]
    result = run_tool(call, store)

    assert response.candidates is not None
    contents.append(response.candidates[0].content)
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_function_response(name=call.name, response={"result": result})],
        )
    )
    final_response = client.models.generate_content(
        model=CHAT_MODEL, contents=contents, config=CONFIG
    )
    return final_response.text or ""


def main() -> None:
    store = build_vector_store()

    questions = [
        "What time is it right now in Tokyo?",
        "How often does Clarence the sourdough starter need feeding at room temperature?",
    ]

    for question in questions:
        print(f"Q: {question}")
        print(f"A: {ask(question, store)}\n")


if __name__ == "__main__":
    main()
