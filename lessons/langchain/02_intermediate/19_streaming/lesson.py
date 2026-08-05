"""
Lesson 19: streaming, showing the answer as it's produced.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/02_intermediate/19_streaming/lesson.py

Every .invoke() call since Lesson 1 has waited for the ENTIRE answer to
be ready before printing anything. This lesson shows the answer
appearing piece by piece instead.
"""

import time

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
prompt = ChatPromptTemplate.from_messages(
    [("human", "Write a short, three-sentence story about a lighthouse keeper.")]
)
chain = prompt | model


def main() -> None:
    # .invoke(): the familiar way. Nothing prints until the ENTIRE reply
    # has arrived, all at once.
    print("Using .invoke() (waits for the whole reply):")
    start = time.time()
    result = chain.invoke({})
    print(f"(waited {time.time() - start:.2f}s before seeing anything)")
    print(result.text)

    # .stream(): instead of one final AIMessage, this hands back an
    # iterator, something you loop over, that produces small CHUNKS of
    # the reply as they become available, before the model is even done
    # generating the rest.
    print("\nUsing .stream() (prints as chunks arrive):")
    start = time.time()
    first_chunk_time = None
    for chunk in chain.stream({}):
        if first_chunk_time is None:
            first_chunk_time = time.time() - start
        # end="" avoids a newline after every chunk, so the words run
        # together into one flowing line, like a typewriter.
        print(chunk.text, end="", flush=True)
    print(f"\n(first chunk arrived after {first_chunk_time:.2f}s)")


if __name__ == "__main__":
    main()
