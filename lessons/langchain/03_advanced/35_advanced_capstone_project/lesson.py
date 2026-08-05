"""
Lesson 35: Advanced Capstone - Local Research Assistant Agent.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/03_advanced/35_advanced_capstone_project/lesson.py

No new concepts. This ties together the entire course into one agent:
- tools, including RAG over local notes (Lessons 13-15, 27-29)
- checkpointer memory (Lessons 23-24)
- automatic conversation summarization for long sessions (Lessons 25-26)
- a human-in-the-loop approval gate before a risky tool (Lesson 30)
- basic tracing (Lesson 34)

Type "quit" to exit.
"""

import ast
import operator
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

# --- Tools: calculator (Lessons 13-14) -----------------------------------

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


# --- Tool: RAG over local notes (Lessons 27-29) --------------------------

NOTES_PATH = Path(__file__).parent / "data" / "notes.txt"


def build_vector_store() -> InMemoryVectorStore:
    text = NOTES_PATH.read_text()
    document = Document(page_content=text, metadata={"source": str(NOTES_PATH)})
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    chunks = splitter.split_documents([document])
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = InMemoryVectorStore(embeddings_model)
    vector_store.add_documents(chunks)
    return vector_store


vector_store = build_vector_store()


@tool
def search_personal_notes(query: str) -> str:
    """Search the user's personal notes (projects, garden, recipes) for
    information relevant to the query."""
    results = vector_store.similarity_search(query, k=2)
    if not results:
        return "No relevant notes found."
    return "\n\n".join(result.page_content for result in results)


# --- Tool: a RISKY action, gated by human-in-the-loop (Lesson 30) -------


@tool
def delete_note_section(topic: str) -> str:
    """Permanently delete the section of the user's notes about a given
    topic. This is IRREVERSIBLE, use with caution."""
    # This is a simulation, nothing is actually deleted. The point of
    # this lesson is the approval gate in front of it, not the action
    # itself.
    return f"(simulated) Deleted the notes section about '{topic}'."


RISKY_TOOLS = {"delete_note_section"}

# --- Basic tracing (Lesson 34), kept lightweight -------------------------


class BasicTracer(BaseCallbackHandler):
    def on_tool_start(self, serialized, input_str, **kwargs) -> None:
        print(f"  [trace] tool call: {serialized.get('name')}({input_str})")


# --- Model, agent, memory, and context management ------------------------

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# SummarizationMiddleware (Lessons 25-26's concept, as a real built-in):
# once the conversation grows past `trigger`, older messages get
# compressed into a summary automatically, instead of growing forever.
summarizer = SummarizationMiddleware(
    model=model,
    trigger=("messages", 12),
    keep=("messages", 4),
)

agent = create_agent(
    model=model,
    tools=[calculator, search_personal_notes, delete_note_section],
    system_prompt=(
        "You are a helpful research assistant with access to a calculator "
        "and the user's personal notes."
    ),
    middleware=[summarizer],
    checkpointer=InMemorySaver(),
    # Pause before EVERY tool call. We only actually ask the user for
    # approval when the requested tool is risky (see handle_turn below),
    # auto-resuming immediately for safe tools like calculator.
    interrupt_before=["tools"],
)


def handle_turn(user_input: str, config: dict, tracer: BasicTracer) -> None:
    result = agent.invoke(
        {"messages": [HumanMessage(user_input)]},
        {**config, "callbacks": [tracer]},
    )

    last_message = result["messages"][-1]
    if not last_message.tool_calls:
        print(f"Agent: {last_message.text}\n")
        return

    risky_calls = [c for c in last_message.tool_calls if c["name"] in RISKY_TOOLS]

    if risky_calls:
        for call in risky_calls:
            print(f"  [approval needed] {call['name']}({call['args']})")
        answer = input("  Approve this action? (yes/no): ").strip().lower()
        if answer not in {"yes", "y"}:
            print("  Rejected, action was not performed.\n")
            return

    # Either no risky tool was requested, or it was just approved:
    # resume the agent so it actually runs the tool(s).
    final = agent.invoke(None, {**config, "callbacks": [tracer]})
    print(f"Agent: {final['messages'][-1].text}\n")


def main() -> None:
    config = {"configurable": {"thread_id": "capstone-demo"}}
    tracer = BasicTracer()

    print("Local Research Assistant. Type 'quit' to exit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break
        if not user_input:
            continue
        handle_turn(user_input, config, tracer)


if __name__ == "__main__":
    main()
