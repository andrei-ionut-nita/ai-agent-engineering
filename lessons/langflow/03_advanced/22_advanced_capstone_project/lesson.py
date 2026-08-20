"""
Lesson 22: Capstone. The same small agent, word-length tool, a
calculator, one Gemini model, built two ways: Langflow (Lesson 16's
flow, unchanged) and raw LangGraph. Same behavior, same tools, same
model, this lesson is about feeling the trade-off directly, not reading
another paragraph about it.

Read README.md in this folder first, then read this file top to bottom,
then run it with (Langflow must still be running from Lesson 1, and
LANGFLOW_API_KEY must be set, see Lesson 7's README):

    uv run python lessons/langflow/03_advanced/22_advanced_capstone_project/lesson.py
"""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

LANGFLOW_URL = "http://127.0.0.1:7860"
HEADERS = {"x-api-key": os.environ["LANGFLOW_API_KEY"]}
LANGFLOW_FLOW_PATH = (
    Path(__file__).parent.parent.parent / "02_intermediate" / "16_intermediate_checkpoint_project" / "flow.json"
)
LANGGRAPH_FILE = Path(__file__).parent / "langgraph_equivalent.py"

QUESTION = "How many letters are in the word 'checkpoint'?"


# --- The Langflow side: Lesson 16's flow, called exactly as it was there ---


def run_via_langflow(question: str) -> str:
    with LANGFLOW_FLOW_PATH.open("rb") as f:
        upload = httpx.post(
            f"{LANGFLOW_URL}/api/v1/flows/upload/",
            headers=HEADERS,
            files={"file": ("flow.json", f, "application/json")},
        )
    upload.raise_for_status()
    flow_id = upload.json()[0]["id"]

    run = httpx.post(
        f"{LANGFLOW_URL}/api/v1/run/{flow_id}",
        headers=HEADERS,
        json={"input_value": question},
        timeout=60,
    )
    run.raise_for_status()
    answer = run.json()["outputs"][0]["outputs"][0]["messages"][0]["message"]

    httpx.delete(f"{LANGFLOW_URL}/api/v1/flows/{flow_id}", headers=HEADERS)
    return answer


# --- The raw LangGraph side: the same two tools, no canvas involved ---


@tool
def word_length(word: str) -> str:
    """Return the number of characters in a single word."""
    return str(len(word))


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '12 * 12'."""
    return str(eval(expression, {"__builtins__": {}}, {}))  # noqa: S307


def run_via_langgraph(question: str) -> str:
    model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    model_with_tools = model.bind_tools([word_length, calculator])

    def call_model(state: MessagesState) -> dict:
        return {"messages": [model_with_tools.invoke(state["messages"])]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode([word_length, calculator]))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    app = graph.compile()

    result = app.invoke({"messages": [{"role": "user", "content": question}]})
    content = result["messages"][-1].content
    if isinstance(content, str):
        return content
    return "".join(block["text"] for block in content if isinstance(block, dict) and block.get("type") == "text")


def main() -> None:
    print(f"Question: {QUESTION}\n")

    langflow_answer = run_via_langflow(QUESTION)
    print(f"Langflow's answer:   {langflow_answer}")

    langgraph_answer = run_via_langgraph(QUESTION)
    print(f"LangGraph's answer:  {langgraph_answer}\n")

    langgraph_loc = len(LANGGRAPH_FILE.read_text().splitlines())
    langflow_flow_bytes = LANGFLOW_FLOW_PATH.stat().st_size
    print(f"langgraph_equivalent.py: {langgraph_loc} lines of Python")
    print(f"Lesson 16's flow.json:   {langflow_flow_bytes:,} bytes of JSON, 0 lines you'd hand-review as code")


if __name__ == "__main__":
    main()
