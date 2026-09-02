"""
Lesson 2: watching naive top-1 retrieval confidently return the wrong
chunk, with real embeddings.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/01_beginner/02_where_naive_retrieval_is_confidently_wrong/lesson.py
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

# This question is deliberately worded in the weather station's own
# vocabulary (SQLite, SD card, sensor readings), so it embeds closest to
# weather-station.md, even though weather-station.md never says where in
# the house the Raspberry Pi actually sits. The real answer lives in
# bookshelf.md, which mentions Project Aurora's Raspberry Pi by name but
# scores lower, because it uses different words to say it.
QUESTION = (
    "Project Aurora's Raspberry Pi writes sensor readings to a SQLite "
    "file on its SD card. Where does that Raspberry Pi physically live "
    "in the house?"
)
CORRECT_SOURCE = "bookshelf.md"


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


def retrieve(query: str, store: list[dict], k: int) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


def generate_answer(query: str, retrieved_chunks: list[dict]) -> str:
    context = "\n\n---\n\n".join(chunk["text"] for chunk in retrieved_chunks)
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {query}"""
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def main() -> None:
    store = build_vector_store()
    print(f"Q: {QUESTION}\n")

    # This is exactly Naive RAG's top-k retrieval, unchanged from
    # naive_rag's Lesson 6, nothing corrective added yet.
    top1 = retrieve(QUESTION, store, k=1)
    print("Naive top-1 retrieval:")
    for chunk in top1:
        marker = "WRONG" if chunk["source"] != CORRECT_SOURCE else "correct"
        print(f"  [{marker}] {chunk['source']} (score={chunk['score']:.4f})")

    print(f"\nGenerated answer from that chunk:\n{generate_answer(QUESTION, top1)}\n")

    # The actual answer, for comparison, so you can see exactly what
    # retrieval missed and why grading (starting Lesson 3) matters.
    correct_chunk = next(record for record in store if record["source"] == CORRECT_SOURCE)
    correct_score = cosine_similarity(embed_texts([QUESTION])[0], correct_chunk["embedding"])
    print(
        f"The correct source, {CORRECT_SOURCE}, scored {correct_score:.4f} "
        f"(ranked below weather-station.md, but well above every other note)."
    )
    print(f"Generated answer from the CORRECT chunk:\n{generate_answer(QUESTION, [correct_chunk])}")
    print(
        "\nNothing about this failure was a low-similarity miss, "
        "weather-station.md scored high because it's genuinely about the "
        "same project. It's just wrong for this specific question. That's "
        "the exact gap Corrective RAG's grading step exists to catch."
    )


if __name__ == "__main__":
    main()
