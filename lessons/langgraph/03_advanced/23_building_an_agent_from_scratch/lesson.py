"""
Lesson 23: building an agent from scratch, the ReAct loop with raw nodes.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/03_advanced/23_building_an_agent_from_scratch/lesson.py

Beginner Lesson 07 built exactly this shape (a model node bound to tools,
a ToolNode, tools_condition looping back). This lesson is that same
pattern grown into something that actually looks like an agent: two
tools, and an explicit framing that this raw graph is what LangChain's
create_agent (langchain course, lesson 23) builds internally.
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


@tool
def word_counter(text: str) -> str:
    """Count how many words are in a piece of text."""
    return str(len(text.split()))


tools = [calculator, word_counter]

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
# bind_tools attaches the tool schemas to every request, so the model can
# respond with a tool call instead of plain text when it decides one is
# needed. This is the one line create_agent does for you without showing
# it; here it's visible.
model_with_tools = model.bind_tools(tools)


def call_model(state: MessagesState) -> dict:
    # Same shape as every model node since Lesson 6: read accumulated
    # messages, call the model on all of them, return the reply.
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("agent", call_model)
# ToolNode inspects the last AIMessage's tool_calls, runs the matching
# Python function(s), and wraps each result in a ToolMessage automatically.
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
# tools_condition reads the last message: if it has tool_calls, route to
# "tools", otherwise route to END. This one conditional edge, plus the
# edge below sending "tools" back to "agent", IS the ReAct loop.
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
app = builder.compile()


def main() -> None:
    # A question that plausibly needs BOTH tools, one after another, so
    # the loop actually runs more than once before landing on END.
    question = (
        "Count the words in the phrase 'the quick brown fox jumps', then "
        "multiply that count by 12."
    )
    result = app.invoke({"messages": [HumanMessage(question)]})

    # Print every message in order, so the loop itself is visible: the
    # model deciding to call a tool, the tool's result coming back, and
    # so on, until a final plain-text answer with no more tool calls.
    for message in result["messages"]:
        role = message.__class__.__name__
        if getattr(message, "tool_calls", None):
            for call in message.tool_calls:
                print(f"[{role}] tool call -> {call['name']}({call['args']})")
        else:
            print(f"[{role}] {message.text}")


if __name__ == "__main__":
    main()
