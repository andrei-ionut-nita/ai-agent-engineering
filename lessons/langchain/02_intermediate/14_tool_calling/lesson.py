"""
Lesson 14: handing a tool to a model, and running the ask/run/ask loop.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/02_intermediate/14_tool_calling/lesson.py

Builds directly on Lesson 13: same calculator tool, now actually
connected to a model.
"""

import ast
import operator

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Same calculator tool as Lesson 13. See that lesson's README for why
# ast is used instead of Python's eval().
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

# .bind_tools() doesn't let the model run code. It just describes the
# tool (name, docstring, arguments, exactly what Lesson 13 inspected) to
# the model, so the model can ask for it by name when it decides it
# needs it.
model_with_tools = model.bind_tools([calculator])


def main() -> None:
    messages = [HumanMessage("What is 847293 multiplied by 3821?")]

    # Round 1: ask the question. The model does NOT answer directly, big
    # multiplication is exactly the kind of thing language models get
    # wrong. Instead it replies with a *request* to run the calculator.
    ai_message = model_with_tools.invoke(messages)
    messages.append(ai_message)

    print("Did the model ask to use a tool?", bool(ai_message.tool_calls))
    for call in ai_message.tool_calls:
        print(f"  -> wants to call {call['name']} with {call['args']}")

    # Round 2: we run the tool ourselves (the model can't run code, it
    # can only ask), and hand the result back as a ToolMessage, labeled
    # with which request it's answering (tool_call_id).
    for call in ai_message.tool_calls:
        result = calculator.invoke(call["args"])
        messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

    # Round 3: send the whole conversation (question + tool request +
    # tool result) back so the model can turn the raw number into a
    # normal sentence.
    final_response = model_with_tools.invoke(messages)
    print("\nFinal answer:", final_response.text)


if __name__ == "__main__":
    main()
