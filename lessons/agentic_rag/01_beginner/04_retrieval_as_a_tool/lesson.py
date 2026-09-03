"""
Lesson 4: declaring retrieval itself as a Gemini tool, and watching the
model ask to call it.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/01_beginner/04_retrieval_as_a_tool/lesson.py
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
    # This is the real, callable Python function Lesson 3's
    # get_current_temperature never had, everything from naive_rag's
    # retrieve() plus a plain-text join, so the result is a string the
    # model can read directly once it comes back as a tool result.
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    top_k = scored[:k]
    return "\n\n---\n\n".join(f"[{r['source']}]\n{r['text']}" for r in top_k)


# The declaration Gemini actually sees. Only the name, description, and
# parameter schema, search_notes() itself (the real function above)
# never crosses this boundary.
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


def main() -> None:
    store = build_vector_store()
    question = "How often does Clarence the sourdough starter need feeding at room temperature?"

    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=question,
        config=types.GenerateContentConfig(tools=[RETRIEVAL_TOOL]),
    )

    print(f"Q: {question}\n")

    calls = response.function_calls
    if calls:
        call = calls[0]
        print(f"Gemini requested: {call.name}(query={call.args.get('query')!r})\n")

        # Manually doing what Lesson 5 automates: actually run the
        # function the model asked for, using the arguments it chose.
        result = search_notes(call.args["query"], store)
        print(f"search_notes() actually returned:\n{result}\n")
        print(
            "Notice Gemini chose its own search query ('sourdough starter\n"
            "feeding schedule' or similar), not necessarily a copy of the\n"
            "original question. This result still isn't the final answer,\n"
            "it's raw tool output. Handing it back to Gemini so it can turn\n"
            "this into a real answer is Lesson 5's job."
        )
    else:
        print(f"Gemini answered directly: {response.text}")


if __name__ == "__main__":
    main()
