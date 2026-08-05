"""
Lesson 21: tracing a LangGraph agent as if it were running in production.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/03_advanced/21_tracing_the_langgraph_agent_in_production/lesson.py

Same agent as Lesson 6 and langgraph course, lesson 23. This lesson
adds what langgraph lesson 32 (tracing_and_observability) covered with
print statements and get_graph() inspection, real production
observability: per-request metadata, tags, and feedback, using actual
LangSmith instead of local debugging.
"""

import ast
import operator
import os
import uuid

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langsmith import Client

load_dotenv()

client = Client()
PROJECT_NAME = os.environ.get("LANGSMITH_PROJECT", "default")

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
    # A tool call is untrusted input from the model: it can produce an
    # expression this parser can't handle (e.g. '^' meaning exponent
    # instead of '**'). Returning an error message, especially in a
    # "production" lesson, lets the agent see that and retry, instead
    # of an unhandled exception crashing the whole request.
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


def handle_request(user_id: str, question: str) -> tuple[str, str]:
    # A per-request run id, exactly Lesson 17's pattern, so feedback can
    # be attached to this specific request's run afterward. metadata
    # carries the user id and an "environment" tag, the two pieces of
    # information every production trace needs to be useful later:
    # who made this request, and where it ran.
    run_id = str(uuid.uuid4())
    result = app.invoke(
        {"messages": [HumanMessage(question)]},
        config={
            "run_name": "production_agent_request",
            "tags": ["langsmith-course", "production"],
            "metadata": {"user_id": user_id, "environment": "production"},
            "run_id": run_id,
        },
    )
    final_message = result["messages"][-1]
    return run_id, final_message.text


def main() -> None:
    requests = [
        ("user-1", "What's 15 multiplied by 4?"),
        ("user-2", "How many words are in 'production tracing matters'?"),
        ("user-1", "What's 100 divided by 5, then squared?"),
    ]

    run_ids = []
    for user_id, question in requests:
        run_id, answer = handle_request(user_id, question)
        run_ids.append(run_id)
        print(f"[{user_id}] {question}\n  -> {answer}")

    # Simulated user feedback on the first request, same mechanism as
    # Lesson 17, now attached to a run produced by a full agent instead
    # of a single traced function.
    client.create_feedback(run_id=run_ids[0], key="user_thumbs_up", score=1)
    print(f"\nPublished feedback on run {run_ids[0]}")

    # Confirms these production requests are findable later, the same
    # filtering approach as Lesson 18, narrowed to this lesson's tag.
    production_runs = list(
        client.list_runs(
            project_name=PROJECT_NAME,
            filter='has(tags, "production")',
            limit=10,
        )
    )
    print(f"Found {len(production_runs)} runs tagged 'production'.")


if __name__ == "__main__":
    main()
