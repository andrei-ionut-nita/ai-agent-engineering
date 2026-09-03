"""
Lesson 18: Intermediate Checkpoint - a multi-turn notes assistant that
retrieves only when needed, across a whole conversation.

No new concepts, this combines Lessons 10-17 into one small script.
Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/02_intermediate/18_intermediate_checkpoint_project/lesson.py
"""

import json
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
HISTORY_PATH = Path(__file__).parent / "conversation_history.json"

SYSTEM_INSTRUCTION = """You answer questions using a search_notes tool that
searches one source document at a time. If a question has more than one
part, call search_notes once per part. When you give your final answer,
cite the source file (shown in brackets, like [sourdough-starter.md])
each fact came from, right after that fact. Only call search_notes for
questions about the personal notes collection it covers, never for
general knowledge questions you can already answer."""


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
        "study journal) for passages relevant to a query. Returns "
        "passages from ONE source document at a time."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"query": types.Schema(type=types.Type.STRING, description="What to search for.")},
        required=["query"],
    ),
)

TOOLS = types.Tool(function_declarations=[SEARCH_NOTES_DECLARATION])
CONFIG = types.GenerateContentConfig(tools=[TOOLS], system_instruction=SYSTEM_INSTRUCTION)


def run_tool_safe(call: types.FunctionCall, store: list[dict]) -> dict[str, str]:
    try:
        args = call.args or {}
        return {"output": search_notes(args["query"], store)}
    except Exception as error:
        return {"error": f"{type(error).__name__}: {error}"}


def ask_turn(contents: list[types.Content], query: str, store: list[dict]) -> str:
    contents.append(types.Content(role="user", parts=[types.Part(text=query)]))

    for _ in range(MAX_STEPS):
        response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=CONFIG)
        calls = response.function_calls
        if not calls:
            assert response.candidates is not None
            contents.append(response.candidates[0].content)
            return response.text or ""

        call = calls[0]
        result = run_tool_safe(call, store)
        assert response.candidates is not None
        contents.append(response.candidates[0].content)
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_function_response(name=call.name, response=result)],
            )
        )

    contents.append(
        types.Content(
            role="model",
            parts=[types.Part(text="I wasn't able to fully answer this within the allowed number of search steps.")],
        )
    )
    return "I wasn't able to fully answer this within the allowed number of search steps."


def save_history(contents: list[types.Content], path: Path) -> None:
    raw = [content.model_dump(mode="json") for content in contents]
    path.write_text(json.dumps(raw, indent=2))


def load_history(path: Path) -> list[types.Content]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text())
    return [types.Content.model_validate(item) for item in raw]


def main() -> None:
    store = build_vector_store()
    if HISTORY_PATH.exists():
        HISTORY_PATH.unlink()

    contents = load_history(HISTORY_PATH)

    conversation = [
        "How often does the sourdough starter need feeding at room temperature?",
        "What's the chemical symbol for gold?",
        "What about it makes it smell like acetone if you skip a feeding?",
        "Where's the pedalboard, and how often should its cables get checked?",
    ]

    for turn_number, question in enumerate(conversation, start=1):
        answer = ask_turn(contents, question, store)
        print(f"Turn {turn_number}")
        print(f"  Q: {question}")
        print(f"  A: {answer}\n")

    save_history(contents, HISTORY_PATH)
    print(f"Saved {len(contents)} turns to {HISTORY_PATH.name}")


if __name__ == "__main__":
    main()
