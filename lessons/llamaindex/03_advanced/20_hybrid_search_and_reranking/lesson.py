"""
Lesson 20: Reranking (and where hybrid search fits conceptually).

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/03_advanced/20_hybrid_search_and_reranking/lesson.py

Vector similarity search (every lesson so far) is fast but approximate:
it ranks Nodes by embedding distance alone, which sometimes surfaces a
Node that's topically nearby but not actually the best answer. A
node_postprocessor runs AFTER retrieval to re-score or filter the
retrieved Nodes before they reach the LLM. This lesson uses LLMRerank,
which asks the LLM itself to re-judge relevance, the cheapest reranker
to demo since it needs no extra model download.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.postprocessor import LLMRerank
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

NIMBUS_DATA_DIR = Path(__file__).parent.parent.parent / "01_beginner" / "02_documents_and_nodes" / "data"
HANDBOOK_DATA_DIR = Path(__file__).parent.parent.parent / "02_intermediate" / "13_multi_document_indexes" / "data"

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)


def node_preview(node_with_score) -> str:
    source = node_with_score.node.metadata.get("file_name", "?")
    text = node_with_score.node.get_content().replace("\n", " ").strip()[:70]
    return f"[{source}] score={node_with_score.score:.4f}  {text}..."


def main() -> None:
    # Two small data sources combined, so the index has more Nodes than
    # the fixture policy files alone, giving retrieval a real chance to
    # pull in a topically-nearby-but-not-best Node worth reranking away.
    documents = SimpleDirectoryReader(str(NIMBUS_DATA_DIR)).load_data()
    documents += SimpleDirectoryReader(str(HANDBOOK_DATA_DIR)).load_data()
    index = VectorStoreIndex.from_documents(documents)

    question = "How many vacation days do new hires get in their first 90 days?"

    # Base retrieval: plain vector similarity, top 3 nodes, no reranking.
    base_retriever = index.as_retriever(similarity_top_k=3)
    base_nodes = base_retriever.retrieve(question)

    print(f"Q: {question}\n")
    print("Base retrieval (similarity_top_k=3, vector distance only):")
    for i, n in enumerate(base_nodes):
        print(f"  {i}. {node_preview(n)}")

    # LLMRerank re-scores the SAME set of retrieved nodes by asking the
    # LLM to judge each one's relevance to the query directly, rather
    # than trusting embedding distance alone. It then keeps only the
    # top_n best-judged nodes. Used as a node_postprocessor, it runs
    # automatically after retrieval and before response synthesis, so
    # the LLM only ever sees the reranked, trimmed set.
    reranker = LLMRerank(top_n=2)
    query_engine = index.as_query_engine(
        similarity_top_k=3,
        node_postprocessors=[reranker],
    )
    response = query_engine.query(question)

    print("\nAfter LLMRerank (top_n=2, LLM re-judges relevance):")
    for i, n in enumerate(response.source_nodes):
        print(f"  {i}. {node_preview(n)}")

    print(f"\nSynthesized answer: {response.response.strip()}")


if __name__ == "__main__":
    main()
