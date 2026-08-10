"""
Lesson 9: Beginner checkpoint project, a small Q&A CLI over the Nimbus
Robotics policy docs.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/01_beginner/09_beginner_checkpoint_project/lesson.py

This ties together every concept from Lessons 1-8 into one small,
usable program: load Documents, split into Nodes, build a VectorStore
Index, wrap it in a ChatEngine, and answer a run of questions against
it, printing both the answer and which source files backed it.

For a reproducible, capturable README, EXAMPLE_QUESTIONS below is a
hardcoded list instead of an input() loop. Swapping in real interactive
input is a two-line change, see run_interactive() at the bottom, not
called by default, but left in place to show how trivial the swap is.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

# Lesson 2's fixture data, reused unchanged by every lesson in this
# section: three short Nimbus Robotics policy .txt files.
DATA_DIR = Path(__file__).parent.parent / "02_documents_and_nodes" / "data"

# Lesson 3's Settings pattern: configure the LLM and embedding model
# once, globally, before building anything.
Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)

# Hardcoded instead of input(), so this lesson's output is exactly
# reproducible for the README. A real CLI would read these from
# input() one at a time instead, see run_interactive() below.
EXAMPLE_QUESTIONS = [
    "What's the vacation policy for new hires?",
    "Can I still take time off if I've used up my first-90-days allowance?",
    "What about expense approval, does it depend on the amount?",
]


def build_engine():
    """Lessons 1-4: Document -> Node -> Index, then Lesson 8: ChatEngine.

    SimpleDirectoryReader loads Documents, VectorStoreIndex.from_documents
    splits them into Nodes and embeds each one (Lessons 2 and 4), and
    as_chat_engine() wraps the result with conversation memory (Lesson
    8), the layer this program actually talks to.
    """
    documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
    index = VectorStoreIndex.from_documents(documents)
    return index.as_chat_engine()


def ask(chat_engine, question: str) -> None:
    """Lesson 8's .chat() call, plus Lesson 5's source_nodes inspection.

    A ChatEngine's response still carries source_nodes, same as a
    QueryEngine's Response did in Lesson 5, so this checkpoint project
    can show both the conversational answer AND which policy files it
    actually came from, tying those two lessons together in one call.
    """
    response = chat_engine.chat(question)
    print(f"You:   {question}")
    print(f"Nimbus Assistant: {response.response.strip()}")

    sources = sorted({Path(n.metadata["file_name"]).name for n in response.source_nodes})
    print(f"  (sources: {', '.join(sources)})\n")


def main() -> None:
    print("Building index over Nimbus Robotics policy docs...\n")
    chat_engine = build_engine()

    print("Running example questions (see run_interactive() for a real input() loop):\n")
    for question in EXAMPLE_QUESTIONS:
        ask(chat_engine, question)


def run_interactive() -> None:
    """Not called by default. A trivial swap from the hardcoded loop
    above: build the engine once, then read questions from the user
    until they quit. Left here to show the shape of a real CLI.
    """
    chat_engine = build_engine()
    print("Nimbus Robotics Q&A. Type a question, or 'quit' to exit.\n")
    while True:
        question = input("You: ").strip()
        if question.lower() in {"quit", "exit"}:
            break
        ask(chat_engine, question)


if __name__ == "__main__":
    main()
