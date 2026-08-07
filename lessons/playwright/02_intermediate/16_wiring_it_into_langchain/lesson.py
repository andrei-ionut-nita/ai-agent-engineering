"""
Lesson 16: wiring the browse tool into LangChain, bound to a Gemini model.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/02_intermediate/16_wiring_it_into_langchain/lesson.py

Builds directly on Lesson 15: the exact same browse(url) function,
unchanged, now wrapped with @tool and handed to a model, following the
same ask/run/respond pattern as Lessons 13-14 of the langchain course.
Requires a GOOGLE_API_KEY in .env, see this course's README.
"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from playwright.sync_api import sync_playwright

load_dotenv()


# The exact same browse function from Lesson 15, unchanged, now with
# @tool added. Nothing inside the function had to change to make it
# usable by a model, that's the whole point of building it plainly
# first: a good tool function doesn't need to know anything about AI.
@tool
def browse(url: str) -> str:
    """Open a URL in a browser and return its visible, readable page text."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url, timeout=15_000)
        except Exception as exc:  # noqa: BLE001 - see Lesson 15's README
            browser.close()
            return f"Could not load {url}: {exc}"

        text = page.locator("body").inner_text()
        browser.close()

        max_chars = 4000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...(truncated)"
        return text


model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# bind_tools() describes browse (its name, docstring, and argument
# schema, the @tool metadata) to the model. It does not give the model
# the power to open a browser itself, the model can only ever ask.
model_with_tools = model.bind_tools([browse])


def main() -> None:
    messages = [
        HumanMessage(
            "What is the text of the first quote on https://quotes.toscrape.com/, "
            "and who said it?"
        )
    ]

    # Round 1: ask the question. The model has no way to know what's on
    # that page, it wasn't part of its training data in any reliable
    # way, and even if it were, the page can change. So instead of
    # guessing, it should reply with a request to call browse.
    ai_message = model_with_tools.invoke(messages)
    messages.append(ai_message)

    print("Did the model ask to use a tool?", bool(ai_message.tool_calls))
    for call in ai_message.tool_calls:
        print(f"  -> wants to call {call['name']} with {call['args']}")

    # Round 2: we actually run the browser ourselves. The model asked,
    # but it cannot open a page, click a button, or touch the network,
    # our code is the only thing that can. This is the same rule from
    # Lesson 14 of the langchain course: the AI decides, your code
    # executes.
    for call in ai_message.tool_calls:
        result = browse.invoke(call["args"])
        messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

    # Round 3: hand the whole conversation, including the raw page text,
    # back to the model so it can pull out just the quote and its
    # author, in a normal sentence.
    final_response = model_with_tools.invoke(messages)
    print("\nFinal answer:", final_response.text)


if __name__ == "__main__":
    main()
