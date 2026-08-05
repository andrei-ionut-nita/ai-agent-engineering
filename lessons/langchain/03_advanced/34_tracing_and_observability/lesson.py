"""
Lesson 34: tracing and observability, seeing what an agent actually did.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/03_advanced/34_tracing_and_observability/lesson.py

Every lesson so far only showed you the FINAL answer. This lesson builds
a small callback handler that logs every step along the way, every
model call and every tool call, with timing, so you can see exactly
what the agent did to arrive at that answer.
"""

import time

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


class TracingHandler(BaseCallbackHandler):
    """A callback handler is an object LangChain calls automatically at
    specific moments (a model call starting, a tool call ending, etc).
    Overriding these methods is how you observe what's happening inside
    an agent, without changing the agent's own code at all."""

    def __init__(self) -> None:
        self._start_times: dict[str, float] = {}

    def on_chat_model_start(self, serialized, messages, *, run_id, **kwargs) -> None:
        self._start_times[str(run_id)] = time.time()
        print(f"[model call started]  ({len(messages[0])} messages in context)")

    def on_llm_end(self, response, *, run_id, **kwargs) -> None:
        elapsed = time.time() - self._start_times.get(str(run_id), time.time())
        print(f"[model call finished] took {elapsed:.2f}s")

    def on_tool_start(self, serialized, input_str, *, run_id, **kwargs) -> None:
        self._start_times[str(run_id)] = time.time()
        tool_name = serialized.get("name", "unknown_tool")
        print(f"[tool started]  {tool_name}({input_str})")

    def on_tool_end(self, output, *, run_id, **kwargs) -> None:
        elapsed = time.time() - self._start_times.get(str(run_id), time.time())
        # `output` is often a ToolMessage object rather than plain text;
        # .content holds the actual result if so.
        result = getattr(output, "content", output)
        print(f"[tool finished] took {elapsed:.2f}s -> {result}")


@tool
def get_word_length(word: str) -> str:
    """Return the number of letters in a word."""
    return str(len(word))


def main() -> None:
    model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    agent = create_agent(model=model, tools=[get_word_length])

    tracer = TracingHandler()

    # config={"callbacks": [...]} attaches our handler to this specific
    # .invoke() call. LangChain then calls our handler's methods
    # automatically at every relevant step, we never call them
    # ourselves.
    result = agent.invoke(
        {"messages": [HumanMessage("How many letters are in the word 'observability'?")]},
        config={"callbacks": [tracer]},
    )

    print("\nFinal answer:", result["messages"][-1].text)


if __name__ == "__main__":
    main()
