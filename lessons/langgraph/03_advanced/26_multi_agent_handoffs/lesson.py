"""
Lesson 26: multi-agent handoffs, one agent routing directly to a peer.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/03_advanced/26_multi_agent_handoffs/lesson.py

Lesson 20 (intermediate tier) introduced Command for updating state and
routing in one step. This lesson uses that exact mechanism for a new
purpose: a "billing" node deciding, mid-conversation, to hand off
straight to a "tech_support" peer node, no central router in between.
Lesson 27 contrasts this with a supervisor-style, centralized approach.
"""

from typing import Literal

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import Command
from pydantic import BaseModel, Field

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


class Routing(BaseModel):
    """A tiny structured decision: can this agent handle the request, or
    does it belong with the other specialist?"""

    handoff_to: Literal["tech_support", "billing", "none"] = Field(
        description="Which specialist this request actually belongs to, or 'none' if the current agent should just answer it."
    )
    reply: str = Field(description="What to say to the user, whether answering directly or explaining the handoff.")


router_model = model.with_structured_output(Routing)


def billing(state: MessagesState) -> Command[Literal["tech_support", "__end__"]]:
    last_text = state["messages"][-1].content
    decision = router_model.invoke(
        f"You are the BILLING agent. A user said: {last_text!r}. "
        "If this is actually a technical problem (bugs, errors, crashes), set "
        "handoff_to='tech_support'. Otherwise handle it yourself and set handoff_to='none'."
    )

    if decision.handoff_to == "tech_support":
        # Command(goto=...) does two things at once: append this agent's
        # note to the shared message history, AND jump straight to the
        # named peer node, bypassing any conditional edge or router.
        return Command(
            goto="tech_support",
            update={"messages": [AIMessage(f"[billing] {decision.reply}")]},
        )

    return Command(goto=END, update={"messages": [AIMessage(f"[billing] {decision.reply}")]})


def tech_support(state: MessagesState) -> Command[Literal["billing", "__end__"]]:
    last_text = state["messages"][-1].content
    decision = router_model.invoke(
        f"You are the TECH SUPPORT agent. A user said: {last_text!r}. "
        "If this is actually a payments/refund/subscription question, set "
        "handoff_to='billing'. Otherwise handle it yourself and set handoff_to='none'."
    )

    if decision.handoff_to == "billing":
        return Command(
            goto="billing",
            update={"messages": [AIMessage(f"[tech_support] {decision.reply}")]},
        )

    return Command(goto=END, update={"messages": [AIMessage(f"[tech_support] {decision.reply}")]})


builder = StateGraph(MessagesState)
builder.add_node("billing", billing)
builder.add_node("tech_support", tech_support)
# Only ONE real edge is declared: the entry point. Every other transition
# (billing -> tech_support, tech_support -> billing, either -> END) is
# decided at runtime by the Command each node returns, not by add_edge or
# add_conditional_edges. This is the defining feature of the handoff
# pattern: peers route to each other directly.
builder.add_edge(START, "billing")
app = builder.compile()


def ask(question: str) -> None:
    result = app.invoke({"messages": [HumanMessage(question)]})
    print(f"Q: {question}")
    for message in result["messages"][1:]:
        print(f"  {message.content}")
    print()


def main() -> None:
    # Starts at billing, and billing itself decides to hand off.
    ask("The app keeps crashing every time I open the settings page.")
    # Starts at billing, and billing can actually handle this one.
    ask("Can I get a refund for last month's subscription?")


if __name__ == "__main__":
    main()
