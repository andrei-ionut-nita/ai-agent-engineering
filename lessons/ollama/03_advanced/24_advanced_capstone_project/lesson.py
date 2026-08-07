"""
Lesson 24 (Capstone): a fully offline RAG agent, no API calls at all.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/03_advanced/24_advanced_capstone_project/lesson.py

This is every idea in this course, combined into one agent:
- Lesson 22's readiness check, before anything else runs.
- Lesson 21's RAG pipeline (split, embed, retrieve), wrapped as a TOOL
  the model can choose to call, instead of always running unconditionally.
- Lesson 17's tool-calling loop, extended with a second, calculator tool.
- Lesson 12's real multi-turn memory, across several questions.
- Lesson 5's streaming, for the final answer the user actually reads.

No .env, no API key, no network call beyond localhost, start to finish.
"""

import math
import time
from pathlib import Path

import ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter

NOTES_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "langchain"
    / "03_advanced"
    / "27_document_loading_and_splitting"
    / "data"
    / "notes.txt"
)

MODEL = "llama3.2"


def wait_for_ollama(timeout_seconds: float = 10.0, poll_interval: float = 0.5) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            ollama.list()
            return
        except ConnectionError:
            time.sleep(poll_interval)
    raise TimeoutError("Ollama did not become reachable in time. Is it running?")


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot_product / (norm_a * norm_b)


class NotesIndex:
    """A tiny in-memory RAG index, built once, searched many times."""

    def __init__(self, path: Path):
        text = path.read_text()
        splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
        self.chunks = splitter.split_text(text)
        self.embeddings = ollama.embed(model="nomic-embed-text", input=self.chunks).embeddings

    def search(self, query: str) -> str:
        query_embedding = ollama.embed(model="nomic-embed-text", input=[str(query)]).embeddings[0]
        ranked = sorted(
            zip(self.chunks, self.embeddings),
            key=lambda pair: cosine_similarity(query_embedding, pair[1]),
            reverse=True,
        )
        return ranked[0][0]


def calculate(expression: str) -> str:
    try:
        return str(eval(str(expression), {"__builtins__": {}}))
    except Exception as exc:
        return f"error: {exc}"


def build_tools(notes: NotesIndex) -> tuple[list[dict], dict]:
    tool_descriptions = [
        {
            "type": "function",
            "function": {
                "name": "search_notes",
                "description": "Search the user's personal notes for relevant information. Call once per distinct topic.",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Evaluate a basic arithmetic expression.",
                "parameters": {
                    "type": "object",
                    "properties": {"expression": {"type": "string"}},
                    "required": ["expression"],
                },
            },
        },
    ]
    functions = {"search_notes": notes.search, "calculate": calculate}
    return tool_descriptions, functions


def run_agent(messages: list[dict], tools: list[dict], functions: dict) -> str:
    while True:
        # Every call streams (Lesson 5), whether or not it ends up
        # requesting a tool. When the model wants a tool, Ollama sends the
        # whole tool_calls list in one early chunk (tool calls aren't
        # streamed token by token); when it's ready to answer directly,
        # content arrives incrementally, chunk by chunk, exactly like
        # Lesson 5, so the user sees the final answer forming live.
        stream = ollama.chat(model=MODEL, messages=messages, tools=tools, stream=True)
        content = ""
        tool_calls = []
        for chunk in stream:
            if chunk.message.tool_calls:
                tool_calls = chunk.message.tool_calls
            if chunk.message.content:
                print(chunk.message.content, end="", flush=True)
                content += chunk.message.content

        if not tool_calls:
            print()
            return content

        messages.append({"role": "assistant", "content": content, "tool_calls": tool_calls})
        for call in tool_calls:
            function = functions[call.function.name]
            result = function(**call.function.arguments)
            print(f"  [tool] {call.function.name}({call.function.arguments}) -> {result[:60]!r}")
            messages.append({"role": "tool", "content": result, "tool_name": call.function.name})


def main() -> None:
    print("Checking Ollama is ready...")
    wait_for_ollama()

    print("Building the notes index (splitting + embedding)...")
    notes = NotesIndex(NOTES_PATH)
    tools, functions = build_tools(notes)

    messages: list[dict] = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant with access to the user's personal "
                "notes via search_notes, and a calculator via calculate. Use tools "
                "when needed, and give a direct final answer once you have enough "
                "information."
            ),
        }
    ]

    print("\nQ1: What practice schedule am I following for cello?")
    messages.append({"role": "user", "content": "What practice schedule am I following for cello?"})
    run_agent(messages, tools, functions)

    print("\nQ2: If I practice that many minutes a day, how many minutes total per week?")
    messages.append(
        {"role": "user", "content": "If I practice that many minutes a day, how many minutes total per week?"}
    )
    run_agent(messages, tools, functions)


if __name__ == "__main__":
    main()
