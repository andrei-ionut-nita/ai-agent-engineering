"""
Lesson 16: tool error handling, when a tool call goes wrong.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/02_intermediate/16_tool_error_handling/lesson.py

So far, every tool call has succeeded. This lesson deliberately asks a
question that makes the calculator fail (division by zero), and shows
the difference between letting that crash the whole program versus
reporting the failure back to the model as a ToolMessage.
"""

import ast
import operator

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

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
model_with_tools = model.bind_tools([calculator])


def ask_without_error_handling(question: str) -> None:
    """The naive version: no try/except around running the tool."""
    messages = [HumanMessage(question)]
    ai_message = model_with_tools.invoke(messages)
    messages.append(ai_message)

    if not ai_message.tool_calls:
        print(ai_message.text)
        return

    for call in ai_message.tool_calls:
        # If calculator.invoke() raises (e.g. dividing by zero), this
        # line crashes the whole program, right here, no matter what
        # else the rest of main() was going to do.
        result = calculator.invoke(call["args"])
        messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

    final_response = model_with_tools.invoke(messages)
    print(final_response.text)


def ask_with_error_handling(question: str) -> None:
    """The robust version: catch the failure, report it, keep going."""
    messages = [HumanMessage(question)]
    ai_message = model_with_tools.invoke(messages)
    messages.append(ai_message)

    if not ai_message.tool_calls:
        print(ai_message.text)
        return

    for call in ai_message.tool_calls:
        try:
            result = calculator.invoke(call["args"])
        except Exception as error:
            # Instead of crashing, we hand the model a ToolMessage
            # describing WHAT went wrong. The model can then react
            # sensibly, explaining the problem, or trying a different
            # approach, instead of our program just dying.
            result = f"Error: {error}"

        messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

    final_response = model_with_tools.invoke(messages)
    print(final_response.text)


def main() -> None:
    broken_question = "Use the calculator tool to compute 4829 divided by 0."

    print("With error handling:")
    ask_with_error_handling(broken_question)

    print("\nWithout error handling (this will crash):")
    ask_without_error_handling(broken_question)


if __name__ == "__main__":
    main()
