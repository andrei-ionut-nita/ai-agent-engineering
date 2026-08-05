"""
Lesson 31: multi-agent supervisor, an agent delegating to other agents.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/03_advanced/31_multi_agent_supervisor/lesson.py

Every tool so far has been a plain function. This lesson wraps two
entire AGENTS as tools, and hands them to a third, "supervisor" agent,
which decides which specialist to delegate each question to.
"""

import ast
import operator

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

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


model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# Two ordinary, fully independent agents, each an expert in one narrow
# domain, exactly like every create_agent since Lesson 23.
math_specialist = create_agent(
    model=model,
    tools=[calculator],
    system_prompt="You are a math specialist. Use the calculator tool for any arithmetic.",
)
text_specialist = create_agent(
    model=model,
    tools=[word_counter],
    system_prompt="You are a text-analysis specialist. Use the word_counter tool when relevant.",
)


# Here's the key idea: wrap each ENTIRE AGENT as a tool. From the
# supervisor's point of view, "ask_math_specialist" looks exactly like
# any other tool, calculator, word_counter, search_personal_notes. It
# has no idea there's a whole separate agent, with its own internal
# tool-call loop, running underneath.
@tool
def ask_math_specialist(question: str) -> str:
    """Delegate a math or arithmetic question to the math specialist agent."""
    result = math_specialist.invoke({"messages": [HumanMessage(question)]})
    return result["messages"][-1].text


@tool
def ask_text_specialist(question: str) -> str:
    """Delegate a text-analysis question (like counting words) to the text specialist agent."""
    result = text_specialist.invoke({"messages": [HumanMessage(question)]})
    return result["messages"][-1].text


# The supervisor never sees calculator or word_counter directly, only
# the two specialist agents, wrapped as tools.
supervisor = create_agent(
    model=model,
    tools=[ask_math_specialist, ask_text_specialist],
    system_prompt=(
        "You are a supervisor. Delegate math questions to ask_math_specialist "
        "and text-analysis questions to ask_text_specialist. Don't answer "
        "those kinds of questions yourself."
    ),
)


def ask(question: str) -> None:
    result = supervisor.invoke({"messages": [HumanMessage(question)]})

    # Which specialist did the supervisor delegate to, if any?
    for message in result["messages"]:
        if getattr(message, "tool_calls", None):
            for call in message.tool_calls:
                print(f"  -> supervisor delegated to: {call['name']}")

    print(f"Q: {question}")
    print(f"A: {result['messages'][-1].text}\n")


def main() -> None:
    ask("What is 156 times 34?")
    ask("How many words are in 'the supervisor delegates to specialists'?")


if __name__ == "__main__":
    main()
