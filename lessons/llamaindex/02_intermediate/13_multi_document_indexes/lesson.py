"""
Lesson 13: Multi-document indexes, one VectorStoreIndex spanning several
unrelated source documents, with per-answer source attribution.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/02_intermediate/13_multi_document_indexes/lesson.py

Uses this lesson's own data/ folder: engineering_handbook.txt (internal
engineering process docs) and product_faq.txt (customer-facing product
FAQ for the Cobalt-1 warehouse robot), two documents about the same
fictional company (Nimbus Robotics) but with no topical overlap, a
realistic shape for "index everything we have, then let retrieval sort
out which document actually answers a given question."
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

DATA_DIR = Path(__file__).parent / "data"

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)


def print_answer_with_sources(query_engine, question: str) -> None:
    """Ask a question and print the answer plus which source file(s)
    backed it, response.source_nodes is where that provenance lives."""
    response = query_engine.query(question)
    sources = sorted({Path(n.metadata["file_name"]).name for n in response.source_nodes})
    print(f"\nQ: {question}")
    print(f"A: {response.response.strip()}")
    print(f"   (sources: {sources})")


def main() -> None:
    # Both files load into ONE list of Documents. Nothing here tells
    # LlamaIndex the two files are "different kinds" of document, they're
    # just two Documents, same as the three Nimbus policy files in earlier
    # lessons were three Documents. The distinction between "engineering
    # handbook" and "product FAQ" only exists in each Node's inherited
    # file_name metadata.
    documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
    print(f"Loaded {len(documents)} documents: "
          f"{sorted(Path(d.metadata['file_name']).name for d in documents)}")

    # One index spans both documents. This is the common case: you don't
    # usually build a separate index per file, you build one index over
    # everything you have and let similarity search find the relevant
    # Nodes regardless of which file they came from.
    index = VectorStoreIndex.from_documents(documents)
    print(f"Index built. Nodes stored: {len(index.docstore.docs)}")

    # This fixture is tiny on purpose (one Node per document, two Nodes
    # total), so the DEFAULT similarity_top_k (2, see llama_index.core.
    # constants.DEFAULT_SIMILARITY_TOP_K) would retrieve BOTH documents on
    # every question regardless of relevance, hiding the thing this lesson
    # wants to show. Setting similarity_top_k=1 here demonstrates
    # retrieval actually distinguishing between the two documents: only
    # the single most relevant Node comes back.
    narrow_query_engine = index.as_query_engine(similarity_top_k=1)

    # A question that should only be answerable from the engineering
    # handbook, product_faq.txt has nothing about code review or on-call.
    print_answer_with_sources(narrow_query_engine, "How many approvals does a pull request need?")

    # A question that should only be answerable from the product FAQ,
    # engineering_handbook.txt has nothing about battery life.
    print_answer_with_sources(narrow_query_engine, "How long does the Cobalt-1's battery last?")

    # A question whose full answer requires combining a fact from each
    # document: the FAQ says a Cobalt-1 enters safe-hold after losing
    # connectivity for 10+ seconds, and the handbook says on-call
    # engineers must acknowledge a page within 15 minutes during business
    # hours. This needs similarity_top_k=2 (the default, used explicitly
    # here for clarity) so both documents' Nodes are retrieved and the
    # query engine can synthesize across them.
    combined_query_engine = index.as_query_engine(similarity_top_k=2)
    print_answer_with_sources(
        combined_query_engine,
        "If a Cobalt-1 loses connectivity and pages the on-call engineer, "
        "how long can it be before someone has to act, combining both the "
        "robot's own safe-hold timeout and the on-call acknowledgment window?",
    )


if __name__ == "__main__":
    main()
