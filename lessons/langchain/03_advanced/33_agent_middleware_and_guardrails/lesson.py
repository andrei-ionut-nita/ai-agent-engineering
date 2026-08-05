"""
Lesson 33: middleware and guardrails, intercepting the agent's own loop.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/03_advanced/33_agent_middleware_and_guardrails/lesson.py

Lesson 30's interrupt_before paused the agent for a HUMAN to approve a
tool call. This lesson runs CODE automatically, before the model is ever
called, to block certain requests outright, no human needed for the
common case.
"""

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import before_model
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


# @before_model wraps a plain function into middleware that runs right
# before every call to the model, with access to the agent's current
# state (including the full message history so far).
@before_model(can_jump_to=["end"])
def block_confidential_requests(state, runtime):
    last_message = state["messages"][-1]

    if "confidential" in last_message.text.lower():
        # Returning {"jump_to": "end", ...} skips the model call
        # entirely for this turn. The agent never sees this request,
        # our own canned message becomes the final answer instead.
        return {
            "jump_to": "end",
            "messages": [
                AIMessage(
                    "I can't help with requests involving confidential information."
                )
            ],
        }

    # Returning None means "no objection", let this turn proceed
    # normally, straight to the model, exactly as if no middleware
    # existed at all.
    return None


model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# middleware=[...] attaches our guardrail to the agent's loop. Every
# single call to this agent runs through block_confidential_requests
# first, automatically, we never have to remember to check manually.
agent = create_agent(model=model, middleware=[block_confidential_requests])


def ask(question: str) -> None:
    result = agent.invoke({"messages": [HumanMessage(question)]})
    print(f"Q: {question}")
    print(f"A: {result['messages'][-1].text}\n")


def main() -> None:
    ask("What is 2 + 2?")
    ask("Tell me the confidential details of the merger.")


if __name__ == "__main__":
    main()
