"""
Lesson 7: response modes, how a QueryEngine turns retrieved Nodes into
one answer.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/01_beginner/07_response_modes/lesson.py

Lesson 5's as_query_engine() used the default synthesis strategy
without naming it. This lesson names it (response_mode="compact") and
runs the same question through two alternatives, refine and
tree_summarize, to see what changes and what a response_mode actually
controls.
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

    question = "What are Nimbus Robotics's rules around expense approval and reimbursement timing?"

    # response_mode controls HOW a QueryEngine turns retrieved Nodes
    # into one final answer, the "synthesize" half of retrieve ->
    # synthesize. Three worth knowing:
    #
    #   "refine" (the oldest strategy): start with the first Node,
    #   generate a draft answer, then for each following Node, show the
    #   LLM the draft PLUS that Node and ask it to refine the draft if
    #   the new Node adds anything. One LLM call per retrieved Node, in
    #   sequence, each call sees the previous answer.
    #
    #   "compact" (the DEFAULT if you don't set response_mode at all,
    #   this is what Lesson 5 used implicitly): pack as much retrieved
    #   Node text as fits into a single prompt as possible, minimizing
    #   the NUMBER of LLM calls, then refine across however many batches
    #   that took. Usually 1 call for small result sets like this
    #   course's data, since 2-3 short Nodes fit in one prompt easily.
    #
    #   "tree_summarize": build a tree of summarization calls,
    #   summarize Nodes in groups, then summarize those summaries, and
    #   so on up to one final answer. Built for LARGE retrieved sets
    #   (dozens+ of Nodes) where even "compact" would need many
    #   sequential refine calls; tree_summarize can run its summarization
    #   calls more in parallel and scales better than "refine" as the
    #   Node count grows.
    #
    # On this course's 3-Node dataset, similarity_top_k defaults to 2,
    # so there's rarely more than 1-2 Nodes to synthesize from at all,
    # meaning these modes will often produce near-identical answers and
    # sometimes an identical number of LLM calls. The differences are
    # real and matter on large retrieved sets; they're just not very
    # visible here. Knowing the modes exist, and why, is the point of
    # this lesson, not seeing dramatically different output.
    modes = ["refine", "compact", "tree_summarize"]

    for mode in modes:
        query_engine = index.as_query_engine(response_mode=mode)
        response = query_engine.query(question)
        print(f"--- response_mode={mode!r} ---")
        print(response.response.strip())
        print()


if __name__ == "__main__":
    main()
