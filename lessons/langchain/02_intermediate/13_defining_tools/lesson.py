"""
Lesson 13: defining a tool, no AI involved yet.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/02_intermediate/13_defining_tools/lesson.py

This lesson is deliberately just Python. No model, no API call. The goal
is to understand what a "tool" actually is, in isolation, before Lesson
14 hands it to an AI.
"""

import ast
import operator

from langchain_core.tools import tool

# Only these operators are allowed. This is deliberately NOT Python's
# built-in eval(), which would let a malicious expression run arbitrary
# code. Restricting to a fixed set of math operators keeps this safe even
# though, in later lessons, the input string will come from an AI, not
# from us directly.
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval(node: ast.AST) -> float:
    # ast.parse() turns a string like "3 + 4 * 2" into a tree of nodes
    # instead of a flat string. This function walks that tree and
    # computes the real value, one node type at a time.
    if isinstance(node, ast.Constant):
        # A bare number, e.g. the "3" in "3 + 4".
        return node.value
    if isinstance(node, ast.BinOp):
        # A two-sided operation, e.g. "3 + 4" (left=3, op=Add, right=4).
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        # A one-sided operation, e.g. the "-" in "-5".
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '12 * (7 + 3)'."""
    tree = ast.parse(expression, mode="eval")
    return str(_eval(tree.body))


def main() -> None:
    # calculator is now a "tool object", not just a plain function. We
    # can still call it directly, no AI involved, by using .invoke()
    # (the same method name every Runnable in LangChain uses) with a
    # dictionary matching its argument name.
    result = calculator.invoke({"expression": "12 * (7 + 3)"})
    print("Result:", result)

    # @tool attached some metadata to our function, which is exactly
    # what an AI will be shown later, in Lesson 14, to decide whether
    # and how to use this tool.
    print("Tool name:", calculator.name)
    print("Tool description:", calculator.description)
    print("Tool arguments schema:", calculator.args)


if __name__ == "__main__":
    main()
