"""
Lesson 15: multiple tools, letting the model choose which one (if any).

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/02_intermediate/15_multiple_tools/lesson.py

Lesson 14 bound exactly one tool. This lesson binds two very different
tools at once, and asks three different kinds of questions, to see the
model pick the right one (or neither) each time.
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


# A second tool, in a completely different domain from the calculator.
# The point of this lesson is having two tools that clearly DON'T
# overlap, so it's obvious which one a given question should trigger.
@tool
def word_counter(text: str) -> str:
    """Count how many words are in a piece of text."""
    return str(len(text.split()))


model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# Both tools bound at once. The model sees descriptions of both, and
# picks whichever (if any) actually fits the question asked.
model_with_tools = model.bind_tools([calculator, word_counter])


def ask(question: str) -> None:
    messages = [HumanMessage(question)]
    ai_message = model_with_tools.invoke(messages)
    messages.append(ai_message)

    print(f"Q: {question}")

    if not ai_message.tool_calls:
        # The model can also choose to use NO tool at all, and just
        # answer directly, exactly like every plain question since
        # Lesson 1.
        print(f"   (no tool used) -> {ai_message.text}\n")
        return

    for call in ai_message.tool_calls:
        print(f"   -> chose tool: {call['name']}({call['args']})")

    # Same manual loop as Lesson 14, generalized: look up which actual
    # function matches each requested tool's name, since more than one
    # tool is available now.
    tools_by_name = {"calculator": calculator, "word_counter": word_counter}
    for call in ai_message.tool_calls:
        chosen_tool = tools_by_name[call["name"]]
        result = chosen_tool.invoke(call["args"])
        messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

    final_response = model_with_tools.invoke(messages)
    print(f"   -> {final_response.text}\n")


def main() -> None:
    ask("What is 84 times 17?")
    ask("How many words are in the sentence: 'The quick brown fox jumps'?")
    ask("What is the capital of France?")


if __name__ == "__main__":
    main()
