"""
Lesson 6: running the exact same agent loop from Lesson 5 against a
question that never needed retrieval, and watching the model skip it.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/01_beginner/06_deciding_not_to_retrieve/lesson.py
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


def ask(query: str, store: list[dict]) -> tuple[str, bool]:
    # Same loop as Lesson 5, unchanged, now returning whether a tool
    # call happened so main() can report it.
    contents: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=query)])
    ]
    response = client.models.generate_content(
        model=CHAT_MODEL, contents=contents, config=CONFIG
    )

    calls = response.function_calls
    if not calls:
        return response.text or "", False

    call = calls[0]
    assert call.name == "search_notes"
    result = search_notes(call.args["query"], store)

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
    return final_response.text or "", True


def main() -> None:
    store = build_vector_store()

    questions = [
        "What is the chemical symbol for gold?",
        "How often does Clarence the sourdough starter need feeding at room temperature?",
    ]

    for question in questions:
        answer, retrieved = ask(question, store)
        print(f"Q: {question}")
        print(f"  Called search_notes(): {retrieved}")
        print(f"  A: {answer}\n")

    print(
        "Same tool, same loop, same code path, both questions. The only\n"
        "difference between the two runs is the model's own judgment about\n"
        "whether it already knew the answer. A misconception worth naming\n"
        "explicitly: nothing forces the model to call a declared tool just\n"
        "because it's available. Declaring a tool makes it *possible* to\n"
        "call, not mandatory, the model still has to decide it's needed,\n"
        "exactly the choice a fixed pipeline was never able to make."
    )


if __name__ == "__main__":
    main()
