"""
Lesson 1: what is Pydantic AI, no agent yet.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/01_beginner/01_what_is_pydantic_ai/lesson.py

There's no pydantic_ai usage yet. This just lays out the vocabulary the
rest of the course builds on.
"""

CORE_IDEA = (
    "An Agent is generic over deps_type (what it can read at runtime) "
    "and output_type (what its final answer must validate against)."
)

LANGCHAIN_MAPPING = {
    "@tool / bind_tools": "@agent.tool (Lessons 6-7)",
    "with_structured_output": "output_type= (Lesson 3)",
    "closures for shared state": "RunContext[Deps].deps (Lesson 5)",
    "LangGraph multi-agent graphs": "agent-as-tool delegation (Lesson 12)",
    "LangSmith datasets/evaluators": "pydantic_evals (Lesson 15)",
    "LangSmith tracing": "OpenTelemetry / Logfire (Lesson 18)",
    "langchain-mcp-adapters": "MCPToolset (Lesson 21)",
}


def main() -> None:
    print("Core idea:")
    print(f"  {CORE_IDEA}")

    print("\nLangChain concept -> Pydantic AI equivalent:")
    for langchain_concept, pydantic_ai_concept in LANGCHAIN_MAPPING.items():
        print(f"  {langchain_concept:<32} -> {pydantic_ai_concept}")


if __name__ == "__main__":
    main()
