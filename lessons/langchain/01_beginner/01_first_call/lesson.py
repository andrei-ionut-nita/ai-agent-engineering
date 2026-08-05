"""
Lesson 1: send one message to an AI and print what it says back.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/01_beginner/01_first_call/lesson.py
"""

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Find the .env file (in the project root) and load GOOGLE_API_KEY from it
# into this program, so the line below can find the key without us typing
# it into the code.
load_dotenv()

# This object knows how to talk to Google's Gemini AI over the internet.
# "gemini-3.5-flash-lite" is the smallest/cheapest model in the Gemini
# 3.5 family, which gives it the highest free-tier request limit, useful
# since we're calling this a lot while learning.
model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


def main() -> None:
    # .invoke() sends the text and waits for the AI's reply.
    response = model.invoke("In one sentence, what is LangChain for?")

    # response is not just text, it's a small package of information.
    # .text is the part of that package that is the AI's written answer.
    print(response.text)


if __name__ == "__main__":
    main()
