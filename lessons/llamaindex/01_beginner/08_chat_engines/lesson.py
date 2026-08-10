"""
Lesson 8: chat engines, retaining memory across turns.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/01_beginner/08_chat_engines/lesson.py

Every QueryEngine call in Lessons 5-7 was stateless: each .query() knew
nothing about any call before it. A ChatEngine adds conversation
memory on top of the same retrieve -> synthesize pipeline, so a
follow-up question like "what about for existing employees?" can be
understood without repeating the original subject.
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

    # as_chat_engine() wraps the same index Lessons 5-7 used, but adds a
    # conversation history the engine consults on every turn. "condense_
    # question" (the default mode used here implicitly) works by first
    # asking the LLM to rewrite the new message into a standalone
    # question using the chat history, e.g. turning "what about for
    # existing employees?" into something like "how much vacation can
    # existing employees use in their first 90 days?", THEN running that
    # rewritten question through the normal retrieve -> synthesize
    # pipeline from Lesson 5. This is why a ChatEngine can answer
    # follow-ups a plain QueryEngine can't: the history is folded into
    # what actually gets retrieved, not just handed to the LLM as extra
    # context.
    chat_engine = index.as_chat_engine()

    turns = [
        "How many vacation days do new hires get to use in their first 90 days?",
        "What about for existing employees, past their first 90 days?",
        "And remind me, how many paid public holidays are there per year?",
    ]

    for message in turns:
        # .chat() is the ChatEngine equivalent of .query(): same
        # underlying retrieve -> synthesize pipeline, but it also reads
        # and appends to the engine's internal chat history, so each
        # call can lean on everything said before it in this loop.
        response = chat_engine.chat(message)
        print(f"User: {message}")
        print(f"Bot:  {response.response.strip()}\n")

    # Contrast with Lessons 5-7: query_engine.query() is stateless, call
    # it twice with the same input and you get the same retrieval and
    # (mode aside) roughly the same answer every time, it never
    # remembers a previous call. chat_engine.chat() is stateful, the
    # SAME engine object accumulates history across calls, which is why
    # the loop above reuses one chat_engine instead of rebuilding it
    # per turn.
    print("query_engine.query() is stateless: no memory between calls (Lessons 5-7).")
    print("chat_engine.chat() is stateful: retains conversation history across calls.")


if __name__ == "__main__":
    main()
