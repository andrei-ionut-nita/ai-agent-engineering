"""
Lesson 1: what is LlamaIndex, and how is it different from LangChain?

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/01_beginner/01_what_is_llamaindex/lesson.py

This lesson makes no network calls. It's a mental-model lesson, fixing
the vocabulary and the framework's core loop in your head before
Lesson 2 introduces Document and Node for real.
"""

# LangChain (already taught in this repo's lessons/langchain course) is
# CHAIN-CENTRIC: you compose arbitrary steps (a prompt, a model call, a
# tool, another model call) into a pipeline or an agent loop. RAG is
# one thing you can build with it, among many.
#
# LlamaIndex is DATA-CENTRIC: the framework's whole design starts from
# one question: "how do I get MY data in front of an LLM, searchable by
# meaning?" Its default path is: ingest documents -> build an index ->
# query it. Agents and tool-calling exist too (Lessons 14-17), but
# they're built on top of that indexing core, not the other way around.
LANGCHAIN_VS_LLAMAINDEX = {
    "Core mental model": "compose arbitrary steps (chains/graphs) vs ingest -> index -> query",
    "RAG's role": "one feature among many vs the default, central use case",
    "Main building block": "Runnable / chain vs Document -> Node -> Index",
    "Config style": "pass objects explicitly through each call vs a global Settings object",
    "Agents": "create_agent, tool-calling loops vs FunctionAgent over QueryEngineTools",
    "Where it shines": "arbitrary multi-step orchestration vs fast, opinionated RAG over documents",
}


def main() -> None:
    print("LangChain (lessons/langchain) vs LlamaIndex (this course):\n")
    for aspect, comparison in LANGCHAIN_VS_LLAMAINDEX.items():
        print(f"  {aspect}:")
        print(f"    {comparison}\n")

    print("This course's core loop, spelled out (Lessons 2-5 build this for real):")
    print("  1. Document   -- your raw source text, e.g. a .txt file")
    print("  2. Node       -- a chunk of a Document, the unit the index actually stores")
    print("  3. Index      -- Nodes plus their embeddings, organized for search")
    print("  4. QueryEngine -- wraps an Index: retrieve relevant Nodes, then ask the LLM")
    print("                     to synthesize an answer from them")

    print(
        "\nNo new setup needed: this course reuses the same GOOGLE_API_KEY "
        "and the same uv-managed .venv as every other course in this repo."
    )


if __name__ == "__main__":
    main()
