"""
Lesson 6: retrievers, the retrieval half of the pipeline, isolated.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/01_beginner/06_retrievers/lesson.py

Lesson 5's query_engine.query() ran retrieve -> synthesize as one call.
This lesson pulls "retrieve" out on its own: index.as_retriever() finds
the most similar Nodes to a question and hands them back raw, with NO
LLM call, only the embedding call needed to embed the question itself.
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
    index = VectorStoreIndex.from_documents(documents)
    print(f"Index built from {len(documents)} documents.\n")

    question = "What is the core collaboration hours window for remote employees?"

    # as_retriever() gives you the retrieval half of Lesson 5's
    # QueryEngine on its own, no synthesis step, no LLM call. This is
    # useful for two reasons: (1) it's cheaper and faster to inspect
    # during development, no reason to pay for an LLM call just to check
    # whether the right Nodes are even being found; (2) it's the piece
    # you'd swap out or tune (top_k, filters, a different retrieval
    # strategy) independently of how answers get synthesized.
    #
    # similarity_top_k controls how many Nodes come back, ranked by
    # similarity to the question's embedding. The QueryEngine default in
    # Lesson 5 was 2 (unstated, just the library default); here it's
    # explicit.
    retriever = index.as_retriever(similarity_top_k=2)

    # .retrieve() takes a plain question string and returns a list of
    # NodeWithScore objects, the exact same type Lesson 5 found inside
    # response.source_nodes. No Response object this time, because
    # there's no synthesized answer, only the raw retrieved evidence.
    results = retriever.retrieve(question)

    print(f"Q: {question}\n")
    print(f"Retrieved {len(results)} nodes (no LLM call made):\n")
    for i, node in enumerate(results):
        source = Path(node.metadata["file_name"]).name
        print(f"--- Result {i} (from {source}, score={node.score:.4f}) ---")
        print(node.text.strip())
        print()

    # Contrast with Lesson 5: a QueryEngine is a Retriever plus a
    # response synthesizer bolted on. index.as_query_engine() builds a
    # retriever internally using the same similarity_top_k idea, then
    # feeds its results into an LLM call to produce response.response.
    # Retrieval alone answers "which Nodes are relevant"; querying
    # answers "what's the answer, based on those Nodes."
    print("as_retriever() = retrieval only, no LLM call.")
    print("as_query_engine() = retrieval + synthesis (Lesson 5), one extra LLM call.")


if __name__ == "__main__":
    main()
