"""
Lesson 2: watching Naive RAG's chunk-and-retrieve loop fail on a
multi-hop question, using this course's own fixture notes.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/01_beginner/02_where_naive_retrieval_fails_multi_hop/lesson.py
"""

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

QUESTION = (
    "Who recalibrated the sensor that Dev flagged as drifting in the "
    "greenhouse, and what tool did they use?"
)
NEEDED_SOURCES = {"greenhouse.md", "maintenance-log.md"}


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    assert response.embeddings is not None
    return [e.values for e in response.embeddings if e.values is not None]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x * x for x in a) ** 0.5
    mag_b = sum(y * y for y in b) ** 0.5
    return dot / (mag_a * mag_b)


def build_vector_store(paths: list[Path]) -> list[dict]:
    texts = [p.read_text() for p in paths]
    vectors = embed_texts(texts)
    return [
        {"source": p.name, "text": t, "embedding": v}
        for p, t, v in zip(paths, texts, vectors)
    ]


def retrieve(query_vector: list[float], store: list[dict], k: int) -> list[dict]:
    ranked = sorted(
        store,
        key=lambda item: cosine_similarity(query_vector, item["embedding"]),
        reverse=True,
    )
    return ranked[:k]


def generate_answer(query: str, retrieved: list[dict]) -> str:
    context = "\n\n---\n\n".join(r["text"] for r in retrieved)
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {query}"""
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def main() -> None:
    paths = sorted(NOTES_DIR.glob("*.md"))
    store = build_vector_store(paths)
    query_vector = embed_texts([QUESTION])[0]

    print(f"Question: {QUESTION}\n")

    retrieved_k2 = retrieve(query_vector, store, k=2)
    sources_k2 = [r["source"] for r in retrieved_k2]
    print(f"k=2 retrieved: {sources_k2}")
    print(f"  Got both needed documents? {NEEDED_SOURCES.issubset(set(sources_k2))}\n")

    retrieved_k4 = retrieve(query_vector, store, k=4)
    sources_k4 = [r["source"] for r in retrieved_k4]
    print(f"k=4 retrieved: {sources_k4}")
    print(f"  Got both needed documents? {NEEDED_SOURCES.issubset(set(sources_k4))}\n")

    print("Answer with k=2 (partial context):")
    print(generate_answer(QUESTION, retrieved_k2))
    print()
    print(
        "Even when k is raised enough to include both documents (k=4 "
        "here), a much larger fraction of the retrieved context is "
        "irrelevant to the question, compared to a graph traversal that "
        "follows the specific relationship connecting the two facts. "
        "Raising k works by including more of everything, not by "
        "understanding which two documents the question actually needs."
    )


if __name__ == "__main__":
    main()
