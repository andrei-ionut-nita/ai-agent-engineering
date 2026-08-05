"""
Lesson 20: langchain-postgres's PGVector, replacing InMemoryVectorStore
from langchain Lesson 28 with a Postgres-backed vector store.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/03_advanced/20_langchain_pgvector_integration/lesson.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

NOTES_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "langchain"
    / "03_advanced"
    / "27_document_loading_and_splitting"
    / "data"
    / "notes.txt"
)
EMBEDDING_DIMENSIONS = 768


def load_and_split() -> list[Document]:
    text = NOTES_PATH.read_text()
    document = Document(page_content=text, metadata={"source": str(NOTES_PATH)})
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    return splitter.split_documents([document])


def main() -> None:
    chunks = load_and_split()

    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        output_dimensionality=EMBEDDING_DIMENSIONS,
    )

    # langchain-postgres uses SQLAlchemy underneath, which expects the
    # "+psycopg" driver suffix on the connection string.
    dsn = os.environ["POSTGRES_DSN"].replace("postgresql://", "postgresql+psycopg://")

    # This is the entire swap from langchain Lesson 28's
    # InMemoryVectorStore: same embeddings_model, same add_documents,
    # same similarity_search afterward, now backed by Postgres.
    vector_store = PGVector(
        embeddings=embeddings_model,
        connection=dsn,
        collection_name="notes",
        pre_delete_collection=True,  # start fresh each run of this lesson
    )
    vector_store.add_documents(chunks)

    # The exact query from langchain Lesson 28: no word overlap with
    # the matching chunk at all.
    query = "What do I know about baking bread at home?"
    results = vector_store.similarity_search(query, k=2)

    print(f"Query: {query}\n")
    print(f"Top {len(results)} most similar chunks (from Postgres, via PGVector):\n")
    for i, result in enumerate(results):
        print(f"--- Match {i + 1} ---")
        print(result.page_content.strip())
        print()


if __name__ == "__main__":
    main()
