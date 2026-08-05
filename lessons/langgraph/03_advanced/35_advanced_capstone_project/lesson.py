"""
Lesson 35: Advanced Capstone, a multi-agent research assistant graph.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/03_advanced/35_advanced_capstone_project/lesson.py

No new mechanisms. This is the whole course's toolbox in one graph: a
supervisor (Lesson 27) routing to two specialist subgraphs (Lesson 19 /
27), tool use inside each specialist (Lesson 23), persistent checkpointer
memory (Lesson 14), and a human-in-the-loop interrupt (Lessons 15 and 30)
before a final, irreversible action. If you can read this file and
explain why every piece is here, you've completed the course.
"""

import ast
import operator
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt
from pydantic import BaseModel, Field
from typing_extensions import Annotated, TypedDict

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# --- Specialist 1: research, backed by a tiny local "search" tool
# (Lesson 29's spirit, kept minimal). ---------------------------------

NOTES = [
    "Photosynthesis converts light energy into chemical energy stored in glucose.",
    "The mitochondria is the organelle responsible for producing most of a cell's ATP.",
    "Newton's second law states that force equals mass times acceleration.",
    "The Krebs cycle occurs in the mitochondrial matrix and produces electron carriers.",
]


@tool
def search_notes(query: str) -> str:
    """Search a small local knowledge base of science notes for relevant facts."""
    words = set(query.lower().split())
    scored = sorted(NOTES, key=lambda n: len(words & set(n.lower().split())), reverse=True)
    top = [n for n in scored[:2] if words & set(n.lower().split())]
    return "\n".join(top) if top else "No relevant notes found."


# --- Specialist 2: calculation (Lesson 23's ReAct loop). -------------

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


def build_specialist(tools: list, system_hint: str):
    # Same from-scratch ReAct shape as Lesson 23, reused for both
    # specialists: a model node bound to tools, a ToolNode, and
    # tools_condition looping back until no more tool calls are needed.
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


research_specialist = build_specialist(
    [search_notes], "You are a research specialist. Use search_notes to find relevant facts."
)
math_specialist = build_specialist(
    [calculator], "You are a math specialist. Use the calculator tool for any arithmetic."
)


# --- Supervisor: classifies each request and routes to a specialist
# (Lesson 27's pattern), OR straight to the report step if the request
# is actually asking to finalize/publish, which needs human approval. ---


class Routing(BaseModel):
    destination: Literal["research", "math", "publish_report"] = Field(
        description="'research' for factual/science questions, 'math' for arithmetic, "
        "'publish_report' if the user is asking to finalize or publish a report."
    )


router_model = model.with_structured_output(Routing)


class CapstoneState(TypedDict):
    # add_messages accumulates across turns, same key shared with both
    # specialist subgraphs, so checkpointer memory (Lesson 14) actually
    # carries the whole conversation forward between separate .invoke()
    # calls in the same thread, not just the latest turn.
    messages: Annotated[list, add_messages]
    destination: str
    report_text: str


def supervisor(state: CapstoneState) -> dict:
    decision = router_model.invoke(state["messages"][-1].content)
    return {"destination": decision.destination}


def route_from_supervisor(state: CapstoneState) -> str:
    return {
        "research": "research_specialist",
        "math": "math_specialist",
        "publish_report": "prepare_report",
    }[state["destination"]]


# --- The irreversible action, gated by a human-in-the-loop interrupt
# (Lessons 15/30's mechanism). -----------------------------------------


def prepare_report(state: CapstoneState) -> dict:
    summary = " ".join(
        m.content if isinstance(m, HumanMessage) else m.text
        for m in state["messages"]
        if isinstance(m, (HumanMessage, AIMessage)) and (m.content if isinstance(m, HumanMessage) else m.text)
    )
    report = f"REPORT SUMMARY:\n{summary[:400]}"
    return {"report_text": report}


def publish_report(state: CapstoneState) -> Command[Literal["__end__"]]:
    # A dynamic breakpoint (Lesson 30): publishing is irreversible, so we
    # always pause here and require an explicit human approval before
    # the "publish" actually happens.
    decision = interrupt(f"About to publish this report:\n{state['report_text']}\n\nApprove? (yes/no)")
    if str(decision).strip().lower() in {"yes", "y"}:
        message = AIMessage(f"Published.\n\n{state['report_text']}")
    else:
        message = AIMessage("Publish cancelled by reviewer.")
    return Command(goto=END, update={"messages": [message]})


builder = StateGraph(CapstoneState)
builder.add_node("supervisor", supervisor)
# Each specialist is a compiled subgraph plugged in as a single node
# (Lesson 19/27's subgraph technique), the supervisor never sees their
# internal tool-call loops.
builder.add_node("research_specialist", research_specialist)
builder.add_node("math_specialist", math_specialist)
builder.add_node("prepare_report", prepare_report)
builder.add_node("publish_report", publish_report)
builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", route_from_supervisor)
builder.add_edge("research_specialist", END)
builder.add_edge("math_specialist", END)
builder.add_edge("prepare_report", "publish_report")


def main() -> None:
    db_path = Path(__file__).parent / "checkpoints.sqlite"
    with SqliteSaver.from_conn_string(str(db_path)) as checkpointer:
        app = builder.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "capstone-session"}}

        # 1. Route to the research specialist.
        r1 = app.invoke(
            {"messages": [HumanMessage("What does the Krebs cycle do?")], "destination": "", "report_text": ""},
            config,
        )
        print("Research:", r1["messages"][-1].text, "\n")

        # 2. Route to the math specialist, in the SAME thread, so
        # checkpointer memory carries the conversation forward.
        r2 = app.invoke({"messages": [HumanMessage("What is 84 divided by 4?")]}, config)
        print("Math:", r2["messages"][-1].text, "\n")

        # 3. Ask to publish a report: this pauses for human approval
        # before the irreversible "publish" step actually runs.
        r3 = app.invoke({"messages": [HumanMessage("Please publish a report of our findings.")]}, config)
        if "__interrupt__" in r3:
            print("[paused for approval]", r3["__interrupt__"][0].value, "\n")
            r3 = app.invoke(Command(resume="yes"), config)
        print("Final:", r3["messages"][-1].text)


if __name__ == "__main__":
    main()
