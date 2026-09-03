"""
Lesson 5: a complete single-step agent loop, model call, tool call (if
requested), tool result handed back, final answer.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/01_beginner/05_a_single_step_agent_loop/lesson.py
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

RETRIEVAL_TOOL = types.Tool(function_declarations=[SEARCH_NOTES_DECLARATION])
CONFIG = types.GenerateContentConfig(tools=[RETRIEVAL_TOOL])


def ask(query: str, store: list[dict]) -> str:
    # Turn 1: the model sees the question and the tool it's allowed to
    # use, and decides whether to answer directly or ask for a call.
    contents: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=query)])
    ]
    response = client.models.generate_content(
        model=CHAT_MODEL, contents=contents, config=CONFIG
    )

    calls = response.function_calls
    if not calls:
        # The model chose not to call anything, this is already the
        # final answer, Lesson 6's exact case.
        return response.text or ""

    # The model asked for exactly one call (this course's tools all
    # take one argument each; a model can in principle request several
    # calls in one turn, out of scope until Lesson 10).
    call = calls[0]
    assert call.name == "search_notes"
    result = search_notes(call.args["query"], store)

    # Turn 2: replay the model's own function-call turn back to it
    # (response.candidates[0].content is exactly that, a Content with
    # role="model" and a function_call part), then attach the tool's
    # result as a new turn with role="user", the shape Gemini's API
    # requires for a function response.
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
    question = "How often does Clarence the sourdough starter need feeding at room temperature?"

    print(f"Q: {question}")
    print(f"A: {ask(question, store)}")


if __name__ == "__main__":
    main()
