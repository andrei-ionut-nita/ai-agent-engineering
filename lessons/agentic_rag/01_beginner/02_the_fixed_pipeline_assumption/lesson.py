"""
Lesson 2: running the fixed, always-retrieve pipeline every prior course
used, against a question that never needed retrieval at all.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/01_beginner/02_the_fixed_pipeline_assumption/lesson.py
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


def retrieve(query: str, store: list[dict], k: int = 2) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


def fixed_pipeline_ask(query: str, store: list[dict]) -> str:
    # This is the entire shape of naive_rag through corrective_rag:
    # retrieve first, unconditionally, then generate. No branch anywhere
    # that asks "does this question even need retrieval?"
    retrieved = retrieve(query, store)
    context = "\n\n---\n\n".join(chunk["text"] for chunk in retrieved)
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {query}"""
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def main() -> None:
    store = build_vector_store()

    questions = [
        "What temperature does water boil at, at sea level, in Celsius?",
        "How often does Clarence the sourdough starter need feeding at room temperature?",
    ]

    for question in questions:
        print(f"Q: {question}")
        answer = fixed_pipeline_ask(question, store)
        print(f"A: {answer}\n")

    print(
        "Both questions paid the exact same cost: one embedding call for the\n"
        "question, one similarity search across every fixture note. For the\n"
        "boiling-point question, that cost bought nothing, Gemini already knew\n"
        "the answer without any of it, and the retrieved sourdough/aquarium/\n"
        "vinyl notes it got stuffed with were irrelevant noise it had to ignore.\n"
        "For the sourdough question, that same cost was exactly what made the\n"
        "correct answer possible at all.\n"
    )
    print(
        "The fixed pipeline can't tell these two cases apart, it doesn't have\n"
        "a way to ask the question. Lesson 3 introduces the mechanism, Gemini\n"
        "function calling, that lets the model ask it instead."
    )


if __name__ == "__main__":
    main()
