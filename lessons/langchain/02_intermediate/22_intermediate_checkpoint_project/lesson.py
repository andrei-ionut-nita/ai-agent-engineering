"""
Lesson 22: Intermediate checkpoint - CLI Assistant with a Tool and Memory.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/02_intermediate/22_intermediate_checkpoint_project/lesson.py

No new concepts. This combines the manual tool-call loop (Lessons 13-16),
manual conversation memory (Lesson 17), structured output (Lesson 18),
and retry handling (Lesson 21) into one small CLI assistant, all built
by hand, with no create_agent yet, that's the Advanced tier.

Type "summary" at any point to get a structured wrap-up of the
conversation so far. Type "quit" to exit.
"""

import ast
import operator
import time

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

load_dotenv()

# --- Tools (Lessons 13-15) ---------------------------------------------

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


TOOLS_BY_NAME = {"calculator": calculator, "word_counter": word_counter}

# --- Structured output schema (Lesson 18) -------------------------------


class ConversationSummary(BaseModel):
    """A structured wrap-up of the conversation so far."""

    topics_discussed: list[str] = Field(description="Short list of topics covered")
    overall_tone: str = Field(description="One word describing the conversation's tone")


# --- Model + retry wrapper (Lesson 21) -----------------------------------

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", max_retries=3)
model_with_tools = model.bind_tools([calculator, word_counter])
structured_model = model.with_structured_output(ConversationSummary)


def invoke_with_retry(runnable, payload, max_attempts: int = 3):
    wait_seconds = 1.0
    for attempt in range(1, max_attempts + 1):
        try:
            return runnable.invoke(payload)
        except Exception as error:
            if attempt == max_attempts:
                raise
            print(f"  (call failed: {error}, retrying in {wait_seconds}s...)")
            time.sleep(wait_seconds)
            wait_seconds *= 2


# --- Main loop: tools + memory + error handling, all combined -----------


def handle_turn(history: list) -> None:
    ai_message = invoke_with_retry(model_with_tools, history)
    history.append(ai_message)

    if not ai_message.tool_calls:
        print(f"Assistant: {ai_message.text}\n")
        return

    for call in ai_message.tool_calls:
        chosen_tool = TOOLS_BY_NAME[call["name"]]
        try:
            # Lesson 16: never let a bad tool call crash the whole loop.
            result = chosen_tool.invoke(call["args"])
        except Exception as error:
            result = f"Error: {error}"
        history.append(ToolMessage(content=result, tool_call_id=call["id"]))

    final_response = invoke_with_retry(model_with_tools, history)
    history.append(final_response)
    print(f"Assistant: {final_response.text}\n")


def print_summary(history: list) -> None:
    # tool_calls_made is computed directly from history, in plain
    # Python, not asked of the model. The model has no reliable way to
    # know this exactly, counting is something code should do, not
    # something to trust a language model to guess correctly.
    tool_calls_made = sum(len(m.tool_calls) for m in history if isinstance(m, AIMessage))

    # topics_discussed and overall_tone genuinely need language
    # understanding, that's what we ask the structured-output call for.
    transcript = "\n".join(
        f"{type(m).__name__}: {m.text}"
        for m in history
        if isinstance(m, (HumanMessage, AIMessage))
    )
    summary = invoke_with_retry(
        structured_model, f"Summarize this conversation:\n{transcript}"
    )
    print("--- Summary ---")
    print("Topics:", ", ".join(summary.topics_discussed))
    print("Tool calls made:", tool_calls_made)
    print("Tone:", summary.overall_tone)
    print()


def main() -> None:
    history: list = []
    print("CLI assistant with a calculator and word counter.")
    print("Type 'summary' for a wrap-up, 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break
        if not user_input:
            continue
        if user_input.lower() == "summary":
            print_summary(history)
            continue

        history.append(HumanMessage(user_input))
        handle_turn(history)


if __name__ == "__main__":
    main()
