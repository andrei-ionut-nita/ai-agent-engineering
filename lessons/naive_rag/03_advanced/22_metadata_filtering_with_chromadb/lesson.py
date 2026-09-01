"""
Lesson 22: narrowing a chromadb query with a metadata filter.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/03_advanced/22_metadata_filtering_with_chromadb/lesson.py
"""

from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768

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


# Every fixture note is about something that happens in one of two
# household areas; tagging that lets a query scope itself to just one.
STUDY_TOPICS = {"bookshelf", "cello-practice", "weather-station"}


def build_collection() -> chromadb.Collection:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)
    areas = ["study" if path.stem in STUDY_TOPICS else "outdoors" for path in paths]

    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="notes")
    collection.add(
        ids=[path.stem for path in paths],
        documents=texts,
        embeddings=vectors,
        metadatas=[{"source": path.name, "area": area} for path, area in zip(paths, areas)],
    )
    return collection


def main() -> None:
    collection = build_collection()

    query = "What's the best way to get a crispy pizza crust?"
    query_vector = embed_texts([query])[0]

    unfiltered = collection.query(query_embeddings=[query_vector], n_results=1)
    print(f"Unfiltered top match: {unfiltered['ids'][0]}")

    # A metadata filter narrows the candidate pool before ranking,
    # exactly the same idea as Lesson 12's Python-level filter, this
    # time expressed as a chromadb `where` clause instead of a list
    # comprehension.
    filtered = collection.query(
        query_embeddings=[query_vector],
        n_results=1,
        where={"area": "study"},
    )
    print(f"Filtered to area='study': {filtered['ids'][0]}")


if __name__ == "__main__":
    main()
