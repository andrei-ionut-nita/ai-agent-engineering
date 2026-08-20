"""
The raw LangGraph version of Lesson 16's flow: one Gemini model, two
tools (word_length, calculator), an agent loop deciding when to call
them. No canvas, no flow.json, just this file. Read it side by side
with lessons/langflow/02_intermediate/16_intermediate_checkpoint_project/flow.json,
this is the comparison this lesson is about.

Run it directly:

    uv run python lessons/langflow/03_advanced/22_advanced_capstone_project/langgraph_equivalent.py
"""

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()


@tool
def word_length(word: str) -> str:
    """Return the number of characters in a single word."""
    return str(len(word))


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '12 * 12'."""
    return str(eval(expression, {"__builtins__": {}}, {}))  # noqa: S307


def build_graph():
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
    return graph.compile()


def extract_text(content) -> str:
    if isinstance(content, str):
        return content
    return "".join(block["text"] for block in content if isinstance(block, dict) and block.get("type") == "text")


def main() -> None:
    app = build_graph()
    result = app.invoke({"messages": [{"role": "user", "content": "How many letters are in the word 'checkpoint'?"}]})
    print(extract_text(result["messages"][-1].content))


if __name__ == "__main__":
    main()
