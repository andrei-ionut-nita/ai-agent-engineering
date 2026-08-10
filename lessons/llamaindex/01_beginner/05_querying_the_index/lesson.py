"""
Lesson 5: querying the index with a QueryEngine.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/01_beginner/05_querying_the_index/lesson.py

Reuses the same data/ folder from Lesson 2 (Nimbus Robotics policy docs)
and builds the same VectorStoreIndex Lesson 4 did. This lesson takes the
last step of the core loop: Index -> QueryEngine, and actually asks it
questions.
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

    # as_query_engine() wraps the index in a QueryEngine, the piece
    # Lesson 4 said an Index doesn't have on its own. Under the hood it
    # does two things when you call .query(): (1) retrieve, embed the
    # question and find the most similar Nodes in the index; (2)
    # synthesize, hand those Nodes to Settings.llm and ask it to answer
    # the question using only that retrieved text. This retrieve-then-
    # synthesize split matters, Lesson 6 shows retrieve alone with no
    # LLM call at all.
    query_engine = index.as_query_engine()

    questions = [
        "How many vacation days do new hires get to use in their first 90 days?",
        "What is the one-time home office equipment stipend, and how long do I have to submit receipts?",
    ]

    for question in questions:
        # .query() runs the full retrieve -> synthesize pipeline and
        # returns a Response object, not a plain string.
        response = query_engine.query(question)

        print(f"Q: {question}")
        # .response is the synthesized answer text, the part you'd show
        # a user.
        print(f"A: {response.response}\n")

        # .source_nodes is the list of Nodes the synthesizer was actually
        # given, each wrapped with a .score (how similar it was to the
        # question's embedding) and the original Node's .metadata (which
        # file it came from). This is what lets you cite sources or debug
        # a wrong answer, seeing exactly what the LLM was shown.
        print("  Source nodes used:")
        for node in response.source_nodes:
            source = Path(node.metadata["file_name"]).name
            print(f"    - {source} (score={node.score:.4f})")
        print()


if __name__ == "__main__":
    main()
