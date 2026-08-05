"""
Lesson 24: giving the agent real memory with a checkpointer.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/03_advanced/24_agent_memory_checkpointer/lesson.py

Builds directly on Lesson 23: same agent, now with a checkpointer added,
so it remembers earlier turns automatically instead of us managing a
messages list by hand like in Lesson 17.
"""

import ast
import operator

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '12 * (7 + 3)'."""
    tree = ast.parse(expression, mode="eval")
    return str(_eval(tree.body))


model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# checkpointer=InMemorySaver() gives the agent real memory: every message
# that passes through gets saved, keyed by a "thread_id" (think:
# conversation id). We never touch a messages list by hand like in
# Lesson 17, we just tell it which thread_id we're continuing.
agent = create_agent(
    model=model,
    tools=[calculator],
    system_prompt="You are a helpful assistant with access to a calculator tool.",
    checkpointer=InMemorySaver(),
)


def main() -> None:
    # Every call tagged with this thread_id shares the same remembered
    # history. A different thread_id would start a brand new, unrelated
    # conversation, even using the same `agent` object.
    config = {"configurable": {"thread_id": "lesson-24-demo"}}

    print("Chat with the agent. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break
        if not user_input:
            continue

        # Notice: we only send THIS turn's new message, not the whole
        # history like Lesson 17. The checkpointer already has
        # everything earlier, tagged under this thread_id, and prepends
        # it for us automatically.
        result = agent.invoke({"messages": [HumanMessage(user_input)]}, config)

        print(f"Agent: {result['messages'][-1].text}\n")


if __name__ == "__main__":
    main()
