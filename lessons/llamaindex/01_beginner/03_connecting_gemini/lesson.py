"""
Lesson 3: connecting Gemini via the global Settings object.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/01_beginner/03_connecting_gemini/lesson.py

This is the first lesson that actually calls Gemini. It also introduces
LlamaIndex's Settings pattern, a real difference from LangChain's style
of passing model objects explicitly into every call.
"""

import os

from dotenv import load_dotenv

# GoogleGenAI is LlamaIndex's LLM wrapper for Gemini, the rough
# equivalent of LangChain's ChatGoogleGenerativeAI.
from llama_index.core import Settings
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()

API_KEY = os.environ["GOOGLE_API_KEY"]


def main() -> None:
    # In LangChain, you build a model object and pass it explicitly into
    # every chain, agent, or call: ChatGoogleGenerativeAI(...), then
    # model.invoke(...). LlamaIndex instead has ONE global object,
    # Settings, that most of the framework reads from automatically: set
    # Settings.llm and Settings.embed_model once, and every Index,
    # QueryEngine, and Agent you build afterward picks them up without
    # you passing them in by hand each time. You CAN still override per
    # call (later lessons do), but the global is the default.
    Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
    Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)

    print("Settings configured:")
    print(f"  Settings.llm: {type(Settings.llm).__name__} (model={Settings.llm.model})")
    print(f"  Settings.embed_model: {type(Settings.embed_model).__name__} (model={Settings.embed_model.model_name})")

    # A direct .complete() call on the LLM, bypassing any index, just to
    # prove the connection works before Lesson 4 builds a real index on
    # top of it. This is the same idea as Lesson 1's first .invoke() call
    # in the langchain course.
    response = Settings.llm.complete("In one short sentence, what is a vector embedding?")
    print(f"\nDirect LLM call:\n  {response.text.strip()}")

    # A direct embedding call: turns one string into a list of floats.
    # We only print the length and a few numbers, the full vector is a
    # few thousand floats long and not useful to read.
    embedding = Settings.embed_model.get_text_embedding("hello world")
    print(f"\nDirect embedding call:")
    print(f"  vector length: {len(embedding)}")
    print(f"  first 5 values: {[round(v, 4) for v in embedding[:5]]}")


if __name__ == "__main__":
    main()
