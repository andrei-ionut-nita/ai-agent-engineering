"""
Lesson 30: human-in-the-loop, pausing before a risky action.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/03_advanced/30_human_in_the_loop/lesson.py

Every agent so far has run its tools immediately, no questions asked.
This lesson pauses the agent right before it would run a tool, shows a
human the exact request, and only continues if approved.
"""

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()


# A tool standing in for something genuinely risky, sending an email
# can't be undone once it happens, unlike a calculator's harmless math.
@tool
def send_email(to: str, body: str) -> str:
    """Send an email to someone."""
    return f"Email sent to {to}: {body}"


model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# interrupt_before=["tools"] tells the agent to PAUSE right before
# entering the "tools" step of its internal graph, every time, no
# matter which tool was requested. A checkpointer is required, pausing
# and resuming later only works if the agent's state is actually saved
# somewhere in between.
agent = create_agent(
    model=model,
    tools=[send_email],
    checkpointer=InMemorySaver(),
    interrupt_before=["tools"],
)


def run_with_approval(question: str, thread_id: str, approve: bool) -> None:
    config = {"configurable": {"thread_id": thread_id}}

    # First call: runs up to the pause point, then stops. It does NOT
    # run the tool yet, no matter what the model decided to request.
    result = agent.invoke({"messages": [HumanMessage(question)]}, config)

    last_message = result["messages"][-1]
    if not last_message.tool_calls:
        # The model didn't need a tool at all, nothing to approve.
        print(f"Q: {question}\nA: {last_message.text}\n")
        return

    for call in last_message.tool_calls:
        print(f"Q: {question}")
        print(f"   PAUSED: agent wants to call {call['name']}({call['args']})")

    if approve:
        # Resuming with None as the input means "continue from exactly
        # where you paused", the agent now actually runs the tool.
        print("   -> approved, resuming...")
        final = agent.invoke(None, config)
        print(f"   -> {final['messages'][-1].text}\n")
    else:
        print("   -> rejected, tool was never run.\n")


def main() -> None:
    run_with_approval(
        "Send an email to bob@example.com saying the meeting is at 3pm.",
        thread_id="approved-demo",
        approve=True,
    )
    run_with_approval(
        "Send an email to everyone@company.com announcing layoffs.",
        thread_id="rejected-demo",
        approve=False,
    )


if __name__ == "__main__":
    main()
