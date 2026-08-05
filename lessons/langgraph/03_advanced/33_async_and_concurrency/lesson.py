"""
Lesson 33: ainvoke/astream, running independent graph calls concurrently.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/03_advanced/33_async_and_concurrency/lesson.py

Every .invoke() since Lesson 1 has been synchronous: your program sits
idle waiting for the network reply. This lesson uses .ainvoke() instead,
and asyncio.gather to run several independent graph calls AT THE SAME
TIME, showing a real wall-clock improvement over calling them one after
another.
"""

import asyncio
import time

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, MessagesState, StateGraph

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


def chatbot(state: MessagesState) -> dict:
    # Nodes themselves can stay written the same way as every earlier
    # lesson; LangGraph runs them via .ainvoke()/.astream() from the
    # outside without requiring an "async def" node function here.
    response = model.invoke(state["messages"])
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)
app = builder.compile()

QUESTIONS = [
    "In one sentence, what is a for loop?",
    "In one sentence, what is a hash map?",
    "In one sentence, what is recursion?",
]


async def ask_async(question: str) -> str:
    # .ainvoke() is the async twin of .invoke(): same graph, same
    # result shape, but it awaits the network call instead of blocking
    # the whole program while waiting.
    result = await app.ainvoke({"messages": [HumanMessage(question)]})
    return result["messages"][-1].text


async def run_sequential() -> float:
    start = time.perf_counter()
    for question in QUESTIONS:
        await ask_async(question)
    return time.perf_counter() - start


async def run_concurrent() -> float:
    start = time.perf_counter()
    # asyncio.gather starts all three .ainvoke() calls essentially at
    # once. Each one spends most of its time waiting on the network, and
    # while one is waiting, the others can be waiting too, instead of
    # queued up behind each other.
    await asyncio.gather(*(ask_async(question) for question in QUESTIONS))
    return time.perf_counter() - start


async def main() -> None:
    sequential_time = await run_sequential()
    print(f"Sequential (await, one at a time): {sequential_time:.2f}s")

    concurrent_time = await run_concurrent()
    print(f"Concurrent (asyncio.gather):        {concurrent_time:.2f}s")

    print(f"\nConcurrent was {sequential_time / concurrent_time:.1f}x faster for {len(QUESTIONS)} calls.")


if __name__ == "__main__":
    asyncio.run(main())
