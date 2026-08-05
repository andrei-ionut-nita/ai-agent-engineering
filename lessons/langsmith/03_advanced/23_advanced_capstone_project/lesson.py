"""
Lesson 23: Advanced Capstone - Fully Instrumented Agent.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/03_advanced/23_advanced_capstone_project/lesson.py
"""

import ast
import operator
import os
import sys
import uuid

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langsmith import Client
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run

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
    # instead of '**'). Returning an error message lets the agent see
    # that and retry, instead of an unhandled exception crashing the
    # whole evaluation run.
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


DATASET_NAME = "langsmith-course-agent-qa"
EXAMPLES = [
    {"inputs": {"question": "What's 8 times 7?"}, "outputs": {"answer": "56"}},
    {"inputs": {"question": "How many words are in 'a fully instrumented agent'?"}, "outputs": {"answer": "4"}},
    {"inputs": {"question": "What's 90 divided by 3?"}, "outputs": {"answer": "30"}},
]
BASELINE_PASS_RATE = 0.60


def ensure_dataset() -> None:
    if client.has_dataset(dataset_name=DATASET_NAME):
        return
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Q&A pairs for the langsmith course capstone agent.",
    )
    client.create_examples(dataset_id=dataset.id, examples=EXAMPLES)


def target(inputs: dict) -> dict:
    result = app.invoke(
        {"messages": [HumanMessage(inputs["question"])]},
        config={"tags": ["langsmith-course", "capstone"], "metadata": {"lesson": 23}},
    )
    return {"answer": result["messages"][-1].text}


def answer_contains_reference(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    correct = reference_outputs["answer"] in outputs["answer"]
    return {"key": "correct", "score": correct}


def pass_rate(runs: list[Run], examples: list[Example]) -> dict:
    reference_by_id = {example.id: example.outputs["answer"] for example in examples}
    passed = sum(
        1 for run in runs if reference_by_id[run.reference_example_id] in run.outputs["answer"]
    )
    return {"key": "pass_rate", "score": passed / len(runs)}


def run_evaluation() -> str:
    results = evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[answer_contains_reference],
        summary_evaluators=[pass_rate],
        experiment_prefix="agent-capstone",
        description="Capstone evaluation of the fully instrumented agent.",
    )
    return results.experiment_name


def check_for_regression(experiment_name: str) -> None:
    # Summary evaluator feedback attaches to the experiment itself
    # (run_id=None), not to individual runs, so it isn't in
    # feedback_stats, list_feedback scoped to the session is how it's
    # read back (Lesson 20).
    project = client.read_project(project_name=experiment_name)
    summary_feedback = list(
        client.list_feedback(sessions=[str(project.id)], feedback_key=["pass_rate"])
    )
    score = summary_feedback[0].score
    print(f"pass_rate: {score:.2f} (baseline: {BASELINE_PASS_RATE:.2f})")
    if score < BASELINE_PASS_RATE:
        print("REGRESSION: failing the build.")
        sys.exit(1)
    print("No regression.")


def simulate_production_traffic_and_feedback() -> None:
    run_id = str(uuid.uuid4())
    result = app.invoke(
        {"messages": [HumanMessage("What's 12 times 12?")]},
        config={
            "run_name": "production_agent_request",
            "tags": ["langsmith-course", "capstone", "production"],
            "metadata": {"user_id": "capstone-user", "environment": "production"},
            "run_id": run_id,
        },
    )
    print(f"\nProduction answer: {result['messages'][-1].text}")

    client.create_feedback(run_id=run_id, key="user_thumbs_up", score=1)
    print(f"Published user feedback on run {run_id}")


def main() -> None:
    ensure_dataset()
    experiment_name = run_evaluation()
    check_for_regression(experiment_name)
    simulate_production_traffic_and_feedback()


if __name__ == "__main__":
    main()
