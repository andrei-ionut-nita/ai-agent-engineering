"""
Lesson 6: tracing a LangGraph agent with no code changes.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/01_beginner/06_tracing_a_langgraph_agent/lesson.py

This is the exact same ReAct agent built in langgraph course, lesson 23
(calculator + word_counter, a model node, a ToolNode, tools_condition
looping between them). Nothing about the graph itself changes here, the
whole point of this lesson is that LANGSMITH_TRACING=true is enough.
"""

import ast
import operator

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

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
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '12 * (7 + 3)'."""
    # A tool call is untrusted input from the model, same as user input
    # is untrusted at a real API boundary: the model can (and, e.g. by
    # writing '^' meaning exponent instead of '**') sometimes produce an
    # expression this parser can't handle. Returning an error message
    # lets the agent see that and retry with a corrected expression,
    # instead of an unhandled exception crashing the whole request.
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_eval(tree.body))
    except Exception as exc:
        return f"Error evaluating '{expression}': {exc}"


@tool
def word_counter(text: str) -> str:
    """Count how many words are in a piece of text."""
    return str(len(text.split()))


tools = [calculator, word_counter]
model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
model_with_tools = model.bind_tools(tools)


def call_model(state: MessagesState) -> dict:
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
app = builder.compile()


def main() -> None:
    question = (
        "Count the words in the phrase 'the quick brown fox jumps', then "
        "multiply that count by 12."
    )
    # The only new thing versus langgraph lesson 23: a run_name, tags,
    # and metadata passed through config. None of these are required for
    # tracing to happen (LANGSMITH_TRACING=true alone is enough), they
    # just make the resulting trace easier to find and filter later.
    result = app.invoke(
        {"messages": [HumanMessage(question)]},
        config={
            "run_name": "calculator_word_counter_agent",
            "tags": ["langsmith-course", "langgraph-agent"],
            "metadata": {"lesson": 6},
        },
    )

    for message in result["messages"]:
        role = message.__class__.__name__
        if getattr(message, "tool_calls", None):
            for call in message.tool_calls:
                print(f"[{role}] tool call -> {call['name']}({call['args']})")
        else:
            print(f"[{role}] {message.text}")


if __name__ == "__main__":
    main()
