"""
Lesson 11: Metadata filtering, restricting retrieval to a subset of the index.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/02_intermediate/11_metadata_and_filtering/lesson.py

Reuses the Nimbus Robotics policy data/ folder from Lesson 2
(01_beginner/02_documents_and_nodes/data/). Builds one index over all
three policy files, then shows retrieval with and without a metadata
filter that restricts search to a single file.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

DATA_DIR = Path(__file__).parent.parent.parent / "01_beginner" / "02_documents_and_nodes" / "data"

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)


def main() -> None:
    documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
    index = VectorStoreIndex.from_documents(documents)
    print(f"Index built over {len(documents)} documents: "
          f"{sorted(Path(d.metadata['file_name']).name for d in documents)}")

    question = "How many days of leave does an employee get per year?"

    # Unfiltered retriever: searches across all three policy files. This
    # question is written to plausibly match more than one file (vacation
    # policy has "days", but so might remote work or expense docs mention
    # "per year" limits), so an unfiltered search can surface nodes from
    # files other than the one you actually want.
    print(f"\n--- Unfiltered retrieval for: {question!r} ---")
    unfiltered_retriever = index.as_retriever(similarity_top_k=3)
    unfiltered_nodes = unfiltered_retriever.retrieve(question)
    for node in unfiltered_nodes:
        source = Path(node.metadata["file_name"]).name
        print(f"  score={node.score:.4f}  source={source}")

    # MetadataFilters restricts retrieval to only Nodes whose metadata
    # matches the given condition, applied BEFORE similarity search runs,
    # not as a post-hoc filter on the results. ExactMatchFilter (an alias
    # for MetadataFilter with the default FilterOperator.EQ) checks
    # node.metadata["file_name"] == "vacation_policy.txt" exactly.
    print(f"\n--- Filtered retrieval (file_name == 'vacation_policy.txt') ---")
    vacation_filter = MetadataFilters(
        filters=[ExactMatchFilter(key="file_name", value="vacation_policy.txt")]
    )
    filtered_retriever = index.as_retriever(similarity_top_k=3, filters=vacation_filter)
    filtered_nodes = filtered_retriever.retrieve(question)
    for node in filtered_nodes:
        source = Path(node.metadata["file_name"]).name
        print(f"  score={node.score:.4f}  source={source}")

    # Same filter works on a query engine, not just a raw retriever, since
    # a QueryEngine's retrieval step is exactly this retriever under the
    # hood. Every node it can hand to the LLM for synthesis is guaranteed
    # to come from vacation_policy.txt, useful when you know in advance
    # which document is relevant (e.g. routing by department, or a UI
    # where the user picked a specific file to ask about).
    filtered_query_engine = index.as_query_engine(filters=vacation_filter)
    response = filtered_query_engine.query(question)
    sources = sorted({Path(n.metadata["file_name"]).name for n in response.source_nodes})
    print(f"\nFiltered query engine answer:\n  {response.response.strip()}")
    print(f"  (sources used: {sources})")


if __name__ == "__main__":
    main()
