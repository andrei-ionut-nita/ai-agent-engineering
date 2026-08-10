"""
Lesson 22: Observability with callbacks, seeing what happened inside a query.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/03_advanced/22_observability_with_callbacks/lesson.py

Every query so far has been a black box: call query_engine.query(), get a
Response back, no visibility into how many LLM calls happened, how many
tokens they used, or how long each step took. llama_index.core.callbacks
attaches handlers to Settings.callback_manager that observe every event
(LLM call, embedding call, retrieval, synthesis) as it happens, without
changing any query code at all.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler, TokenCountingHandler
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

DATA_DIR = Path(__file__).parent.parent.parent / "01_beginner" / "02_documents_and_nodes" / "data"

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)


def main() -> None:
    # TokenCountingHandler tallies prompt/completion tokens for every LLM
    # call, and tokens for every embedding call, cumulative across
    # whatever it's attached to for as long as it's attached.
    token_counter = TokenCountingHandler()

    # LlamaDebugHandler keeps a running trace of every event (LLM calls,
    # embedding calls, retrieval, synthesis) with timing, and prints a
    # simple tree of that trace when a top-level trace ends
    # (print_trace_on_end=True, the default).
    llama_debug = LlamaDebugHandler(print_trace_on_end=False)

    # CallbackManager fans events out to every handler passed to it.
    # Setting Settings.callback_manager makes it global, the same
    # pattern as Settings.llm and Settings.embed_model from Lesson 3:
    # set once, everything built afterward (Index, QueryEngine) picks it
    # up automatically, no changes needed to any query code.
    Settings.callback_manager = CallbackManager([token_counter, llama_debug])

    documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
    index = VectorStoreIndex.from_documents(documents)

    print("Index built. Token usage so far (embedding the 3 fixture documents):")
    print(f"  embedding tokens: {token_counter.total_embedding_token_count}")

    query_engine = index.as_query_engine()
    question = "What is Nimbus Robotics' policy on expense reports submitted late?"
    response = query_engine.query(question)

    print(f"\nQ: {question}")
    print(f"A: {response.response.strip()}")

    # Cumulative token counts, embedding tokens now include the question
    # itself too, LLM tokens cover the synthesis call that produced the
    # answer above.
    print("\nCumulative token usage after the query:")
    print(f"  embedding tokens: {token_counter.total_embedding_token_count}")
    print(f"  LLM prompt tokens: {token_counter.prompt_llm_token_count}")
    print(f"  LLM completion tokens: {token_counter.completion_llm_token_count}")
    print(f"  LLM total tokens: {token_counter.total_llm_token_count}")

    # LlamaDebugHandler recorded every event with a start/end pair.
    # get_event_pairs() with no argument returns them all, in order, so
    # this prints the actual sequence of operations the query triggered
    # under the hood: embedding the query, retrieving nodes, calling the
    # LLM to synthesize, etc.
    print("\nEvent trace captured by LlamaDebugHandler:")
    for pair in llama_debug.get_event_pairs():
        event_type = pair[0].event_type.name
        print(f"  {event_type}")


if __name__ == "__main__":
    main()
