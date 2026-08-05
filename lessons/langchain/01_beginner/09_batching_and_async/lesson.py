"""
Lesson 9: batching and async, running more than one call at a time.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/01_beginner/09_batching_and_async/lesson.py
"""

import asyncio
import time

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
prompt = ChatPromptTemplate.from_messages([("human", "In one word, what color is {thing}?")])
chain = prompt | model | StrOutputParser()

# Three DIFFERENT sets of things, one set per method below. Using
# distinct questions for each phase, instead of the same three questions
# three times, matters here: Gemini automatically caches repeated
# identical prompts, which would make a later phase look artificially
# fast for a reason that has nothing to do with batching or async.
sequential_things = ["the sky", "grass", "a banana"]
batched_things = ["a fire truck", "snow", "an eggplant"]
async_things = ["a school bus", "coal", "a flamingo"]


def sequential() -> None:
    # One .invoke() at a time, waiting for each reply before starting
    # the next one. Three separate round trips to Google's servers, one
    # after another.
    start = time.time()
    for thing in sequential_things:
        chain.invoke({"thing": thing})
    print(f"Sequential .invoke() x3: {time.time() - start:.2f}s")


def batched() -> None:
    # .batch() sends all three at once and lets LangChain manage running
    # them concurrently, instead of one at a time. Same three questions,
    # same three answers, but the network round trips overlap instead of
    # queuing up.
    start = time.time()
    chain.batch([{"thing": thing} for thing in batched_things])
    print(f"chain.batch() x3:        {time.time() - start:.2f}s")


async def run_async() -> None:
    # .ainvoke() is the async version of .invoke(). Using asyncio.gather
    # here starts all three at once, similar to what .batch() does, but
    # written using Python's async/await instead of a batch method.
    start = time.time()
    await asyncio.gather(*(chain.ainvoke({"thing": thing}) for thing in async_things))
    print(f"asyncio.gather + ainvoke: {time.time() - start:.2f}s")


def main() -> None:
    sequential()
    batched()
    asyncio.run(run_async())


if __name__ == "__main__":
    main()
