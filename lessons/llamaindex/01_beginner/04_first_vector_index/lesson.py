"""
Lesson 4: building your first VectorStoreIndex.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/01_beginner/04_first_vector_index/lesson.py

Reuses the same data/ folder from Lesson 2 (Nimbus Robotics policy
docs). This is the "index" step of ingest -> index -> query, LlamaIndex's
core loop from Lesson 1.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

DATA_DIR = Path(__file__).parent.parent / "02_documents_and_nodes" / "data"

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)


def main() -> None:
    documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
    print(f"Loaded {len(documents)} documents")

    # VectorStoreIndex.from_documents does three things in one call:
    #   1. Splits every Document into Nodes (using Settings' default
    #      node parser under the hood, a SentenceSplitter, same as
    #      Lesson 2 did explicitly).
    #   2. Calls Settings.embed_model on EVERY node's text, turning each
    #      one into a vector.
    #   3. Stores nodes + vectors together in an in-memory vector store,
    #      ready for similarity search.
    # This one line is doing real work: it makes one embedding API call
    # per node, which is why building an index isn't free, and why
    # Lesson 21 (persisting indexes) matters once your data stops being
    # tiny fixture files.
    index = VectorStoreIndex.from_documents(documents)

    print(f"\nIndex built. Nodes stored: {len(index.docstore.docs)}")

    # Peek under the hood: index.vector_store holds the raw embedded
    # data. Each node's vector has the same dimensionality the
    # embedding model produces (3072 for gemini-embedding-001, same as
    # Lesson 3's direct embedding call).
    first_node_id = next(iter(index.docstore.docs))
    first_node = index.docstore.docs[first_node_id]
    print(f"\nFirst stored node:")
    print(f"  source file: {Path(first_node.metadata['file_name']).name}")
    print(f"  text preview: {first_node.text[:80].strip()}...")

    # An Index by itself just stores things, it doesn't answer
    # questions. Lesson 5 wraps this same index in a QueryEngine, which
    # is the piece that actually retrieves nodes and asks the LLM to
    # synthesize an answer from them.
    print("\nAn Index stores and embeds; it doesn't answer questions on its own.")
    print("Lesson 5 wraps this index in a QueryEngine to actually query it.")


if __name__ == "__main__":
    main()
