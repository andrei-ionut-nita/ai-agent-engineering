"""
Lesson 27: a supervisor graph routing to specialist subgraphs.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/03_advanced/27_multi_agent_supervisor_graph/lesson.py

This is the same idea as multi_agent_supervisor (langchain course, lesson
31), one level lower: specialists here are compiled StateGraphs (Lesson
19's subgraph technique), not create_agent objects, and the supervisor
is a graph node with a conditional edge, not an agent choosing tools.
Contrast with Lesson 26: there, peers handed off to each other directly;
here, one central node decides where every request goes.
"""

import ast
import operator
from typing import Literal

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel, Field
from typing_extensions import Annotated, TypedDict

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

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


def build_specialist(tools: list, system_hint: str):
    # Exactly Lesson 23's from-scratch ReAct loop, one per specialist.
    # Each specialist is its own small, fully independent compiled
    # StateGraph, it has no idea a supervisor exists above it.
    bound_model = model.bind_tools(tools)

    def call_model(state: MessagesState) -> dict:
        response = bound_model.invoke([HumanMessage(system_hint), *state["messages"]])
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    return builder.compile()


math_specialist = build_specialist([calculator], "You are a math specialist, use the calculator tool.")
text_specialist = build_specialist([word_counter], "You are a text specialist, use the word_counter tool.")


class SupervisorState(TypedDict):
    # messages is shared with both specialist subgraphs (same key, same
    # add_messages reducer), that shared key is what lets a compiled
    # subgraph slot in as a node directly. route is extra state the
    # subgraphs never see or touch.
    messages: Annotated[list, add_messages]
    route: str


class Routing(BaseModel):
    specialist: Literal["math", "text"] = Field(
        description="'math' for arithmetic/calculation requests, 'text' for requests about counting or analyzing words in a piece of text."
    )


router_model = model.with_structured_output(Routing)


def supervisor(state: SupervisorState) -> dict:
    decision = router_model.invoke(
        "Classify this request as 'math' (it needs arithmetic) or 'text' (it needs "
        f"word/text analysis): {state['messages'][-1].content!r}"
    )
    return {"route": decision.specialist}


def route_to_specialist(state: SupervisorState) -> Literal["math_specialist", "text_specialist"]:
    return "math_specialist" if state["route"] == "math" else "text_specialist"


builder = StateGraph(SupervisorState)
builder.add_node("supervisor", supervisor)
# A compiled StateGraph plugs in as a node exactly like a plain function
# would. LangGraph runs the whole subgraph internally whenever this node
# is reached, and only the shared "messages" key flows back out to the
# parent's state.
builder.add_node("math_specialist", math_specialist)
builder.add_node("text_specialist", text_specialist)
builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", route_to_specialist)
builder.add_edge("math_specialist", END)
builder.add_edge("text_specialist", END)
app = builder.compile()


def ask(question: str) -> None:
    result = app.invoke({"messages": [HumanMessage(question)], "route": ""})
    print(f"Q: {question}")
    print(f"  routed to: {result['route']}_specialist")
    print(f"  A: {result['messages'][-1].text}\n")


def main() -> None:
    ask("What is 342 times 17?")
    ask("How many words are in 'the supervisor routes to specialists'?")


if __name__ == "__main__":
    main()
