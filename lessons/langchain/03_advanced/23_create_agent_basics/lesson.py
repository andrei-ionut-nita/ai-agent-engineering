"""
Lesson 23: create_agent, automating the tool-call loop.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/03_advanced/23_create_agent_basics/lesson.py

This lesson does NOT add memory yet, that's Lesson 24. Each call here is
still independent, same as every .invoke() since Lesson 1. The only new
thing is that the tool-call loop from Lesson 14 (ask, run the tool, ask
again) now happens automatically, inside one .invoke() call.
"""

import ast
import operator

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Same calculator tool from Lesson 13.
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

# create_agent builds the entire "ask -> maybe call a tool -> ask again"
# loop from Lesson 14 for us, as many rounds as needed, automatically.
# No checkpointer here yet, so this agent has no memory between separate
# .invoke() calls, same as a plain model at this point.
agent = create_agent(
    model=model,
    tools=[calculator],
    system_prompt="You are a helpful assistant with access to a calculator tool.",
)


def main() -> None:
    # One .invoke() call. Internally, this runs the same three rounds
    # from Lesson 14 (ask, run the tool, ask again) without us writing
    # any of that loop by hand.
    result = agent.invoke({"messages": [HumanMessage("What is 293 times 481?")]})

    # result["messages"] is the full conversation for this call,
    # including the tool request and tool result the agent generated
    # along the way. The last entry is always the final answer.
    print("Final answer:", result["messages"][-1].text)

    # A second, separate call. Since there's no memory yet, this has no
    # idea the first question ever happened, it can't know what number
    # was involved.
    result2 = agent.invoke(
        {"messages": [HumanMessage("What numbers did I just ask you to multiply?")]}
    )
    print("Second call:", result2["messages"][-1].text)


if __name__ == "__main__":
    main()
