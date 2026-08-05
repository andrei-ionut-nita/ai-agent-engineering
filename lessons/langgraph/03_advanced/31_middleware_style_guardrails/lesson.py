"""
Lesson 31: guardrail nodes wrapping the real work.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/03_advanced/31_middleware_style_guardrails/lesson.py

This is what @before_model / @after_model middleware (langchain course,
lesson 33) is doing under the hood: extra nodes in the sequence. Here
there's no decorator or hidden wrapping at all, a guardrail is just
another node, wired in with a plain conditional edge before the model,
and a plain edge after it.
"""

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

BANNED_WORDS = {"confidential", "password"}
MAX_INPUT_LENGTH = 300


class State(TypedDict):
    question: str
    blocked_reason: str
    answer: str


def input_guardrail(state: State) -> dict:
    # Runs BEFORE the real work. Two independent, automatic checks, no
    # human review needed for either, and no model call happens at all
    # if either one trips.
    text = state["question"].lower()
    if any(word in text for word in BANNED_WORDS):
        return {"blocked_reason": "request mentions restricted information"}
    if len(state["question"]) > MAX_INPUT_LENGTH:
        return {"blocked_reason": "request is too long"}
    return {"blocked_reason": ""}


def route_after_input_guard(state: State) -> str:
    return "generate" if not state["blocked_reason"] else END


def generate(state: State) -> dict:
    response = model.invoke(state["question"])
    return {"answer": response.text}


def output_guardrail(state: State) -> dict:
    # Runs AFTER the real work, a format check on what the model
    # produced. A real system might check for PII, banned phrases, or
    # required disclaimers here; this one is intentionally simple.
    answer = state["answer"]
    if len(answer) > 800:
        return {"answer": answer[:800] + "... (truncated by output guardrail)"}
    return {}


builder = StateGraph(State)
builder.add_node("input_guardrail", input_guardrail)
builder.add_node("generate", generate)
builder.add_node("output_guardrail", output_guardrail)
builder.add_edge(START, "input_guardrail")
# A guardrail node is a node like any other, its "special" behavior is
# entirely due to WHERE it's wired in: before the model, or after it.
builder.add_conditional_edges("input_guardrail", route_after_input_guard)
builder.add_edge("generate", "output_guardrail")
builder.add_edge("output_guardrail", END)
app = builder.compile()


def ask(question: str) -> None:
    result = app.invoke({"question": question, "blocked_reason": "", "answer": ""})
    print(f"Q: {question}")
    if result["blocked_reason"]:
        print(f"  [blocked before the model was ever called] {result['blocked_reason']}\n")
    else:
        print(f"  A: {result['answer']}\n")


def main() -> None:
    ask("What is 2 + 2?")
    ask("Tell me the confidential details of the merger.")


if __name__ == "__main__":
    main()
