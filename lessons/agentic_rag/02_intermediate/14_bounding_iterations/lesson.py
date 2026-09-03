"""
Lesson 14: a max-steps guard, so the multi-step loop always terminates,
even if the model never stops asking for tool calls.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/02_intermediate/14_bounding_iterations/lesson.py
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
MAX_STEPS = 4


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
    description="Search a personal notes collection for passages relevant to a query.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"query": types.Schema(type=types.Type.STRING, description="What to search for.")},
        required=["query"],
    ),
)

TOOLS = types.Tool(function_declarations=[SEARCH_NOTES_DECLARATION])
CONFIG = types.GenerateContentConfig(tools=[TOOLS])


def ask(query: str, store: list[dict]) -> tuple[str, int, bool]:
    # Returns (answer, steps_used, hit_limit) so main() can report
    # whether the loop finished naturally or was cut off.
    contents: list[types.Content] = [types.Content(role="user", parts=[types.Part(text=query)])]

    for step in range(1, MAX_STEPS + 1):
        response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=CONFIG)
        calls = response.function_calls
        if not calls:
            return response.text or "", step - 1, False

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

    # The loop ran MAX_STEPS times and the model was STILL asking for
    # more calls. Rather than let it run forever, stop here and return
    # an honest "couldn't finish" answer instead of silently returning
    # nothing or crashing.
    return (
        "I wasn't able to fully answer this within the allowed number of "
        "search steps. Here's what I found so far, it may be incomplete.",
        MAX_STEPS,
        True,
    )


def main() -> None:
    store = build_vector_store()

    question = "How often does the sourdough starter need feeding at room temperature?"
    print(f"Q: {question}")
    answer, steps, hit_limit = ask(question, store)
    print(f"  steps used: {steps}/{MAX_STEPS}, hit limit: {hit_limit}")
    print(f"  A: {answer}\n")

    print(
        f"MAX_STEPS is set to {MAX_STEPS} here. A well-behaved question like the\n"
        "one above finishes in one or two steps, comfortably inside that\n"
        "budget. The guard only matters when a question or a tool description\n"
        "leads the model to keep calling without ever concluding it has\n"
        "enough information, Lesson 16 studies exactly that failure mode next."
    )


if __name__ == "__main__":
    main()
