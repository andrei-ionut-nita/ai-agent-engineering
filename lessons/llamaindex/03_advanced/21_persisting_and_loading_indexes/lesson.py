"""
Lesson 21: Persisting and loading indexes, no re-embedding on every run.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/03_advanced/21_persisting_and_loading_indexes/lesson.py

Lesson 4 noted that building a VectorStoreIndex costs one embedding API
call per Node, and that this gets expensive once your data is more than
a few tiny fixture files. StorageContext.persist() writes an index's
Nodes, vectors, and metadata to plain JSON files on disk;
load_index_from_storage() reads them back, reconstructing the exact same
index with zero new embedding calls. This script builds and persists an
index, then reloads it as if from a second process, and queries the
reloaded copy to prove the round trip worked.

This run writes a ./storage/ subfolder next to this file, a build
artifact, not committed course content. Re-running this script is
idempotent: it always rebuilds and re-persists from the same source
documents, overwriting ./storage/ with the same content each time (the
persisted Node IDs will differ per run since they're random UUIDs, but
the text, structure, and query behavior are identical).
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

DATA_DIR = Path(__file__).parent.parent.parent / "01_beginner" / "02_documents_and_nodes" / "data"
STORAGE_DIR = Path(__file__).parent / "storage"

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)


def build_and_persist() -> None:
    """Simulates the first process: build an index and save it to disk."""
    documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
    index = VectorStoreIndex.from_documents(documents)
    print(f"Built index: {len(index.docstore.docs)} nodes (this cost embedding API calls)")

    # persist() writes docstore.json, index_store.json, and
    # default__vector_store.json (Nodes, the index structure, and the
    # embedding vectors, respectively) into persist_dir.
    index.storage_context.persist(persist_dir=str(STORAGE_DIR))
    print(f"Persisted to {STORAGE_DIR}")


def load_and_query() -> None:
    """Simulates a second process: reload the index from disk, no re-embedding."""
    # StorageContext.from_defaults(persist_dir=...) points at the folder
    # written above. load_index_from_storage() reads the JSON files and
    # reconstructs the exact same VectorStoreIndex, Nodes and vectors
    # included, no SimpleDirectoryReader or from_documents() call, and
    # critically, no new embedding API calls for the stored Nodes.
    storage_context = StorageContext.from_defaults(persist_dir=str(STORAGE_DIR))
    reloaded_index = load_index_from_storage(storage_context)
    print(f"\nReloaded index: {len(reloaded_index.docstore.docs)} nodes (zero embedding calls for these)")

    # Querying still costs ONE embedding call, to embed the question
    # itself, that's unavoidable. What's avoided is re-embedding every
    # stored Node, the expensive part that scales with corpus size.
    query_engine = reloaded_index.as_query_engine()
    question = "How many paid public holidays does Nimbus Robotics observe?"
    response = query_engine.query(question)
    print(f"\nQ: {question}")
    print(f"A: {response.response.strip()}")


def main() -> None:
    build_and_persist()
    load_and_query()


if __name__ == "__main__":
    main()
