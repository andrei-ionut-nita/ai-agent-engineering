"""
Lesson 17 (Checkpoint): an agent that searches a site and reports back.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/02_intermediate/17_intermediate_checkpoint_project/lesson.py

This closes out the intermediate tier. Lessons 15 and 16 built and
bound one browse(url) tool, then walked it through exactly one round
of tool use. A real agent often needs more than one round, one page
usually isn't enough to answer a question, it may need to follow a
link, check a second page, then decide it finally has enough
information to answer. This lesson generalizes the ask/run/respond
pattern into a loop that repeats until the model stops asking for
tools.

Requires a GOOGLE_API_KEY in .env, see this course's README.
"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from playwright.sync_api import sync_playwright

load_dotenv()


# The same browse tool from Lessons 15 and 16, unchanged.
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
model_with_tools = model.bind_tools([browse])


def run_agent(question: str, max_rounds: int = 5) -> str:
    """Runs the ask/run/respond loop repeatedly, until the model stops
    asking for tools or we hit max_rounds, whichever comes first.

    max_rounds is a safety limit. Nothing here mathematically guarantees
    the model eventually stops asking for tools, an unclear question or
    a page that never contains the answer could send it looping forever.
    Bounding the number of rounds is a cheap, essential guardrail for
    any agent loop you build outside of a tutorial, too.
    """
    messages: list = [HumanMessage(question)]

    for round_number in range(1, max_rounds + 1):
        ai_message = model_with_tools.invoke(messages)
        messages.append(ai_message)

        if not ai_message.tool_calls:
            # No more tool requests means the model believes it has
            # enough information to answer directly. We're done.
            print(f"(answered after {round_number} round(s))")
            return ai_message.text

        print(f"Round {round_number}: model requested {len(ai_message.tool_calls)} browse call(s)")
        for call in ai_message.tool_calls:
            print(f"  -> browse({call['args'].get('url')!r})")
            result = browse.invoke(call["args"])
            messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

    return (
        f"Gave up after {max_rounds} rounds without a final answer. "
        "The model may need a more specific question, or more rounds."
    )


def main() -> None:
    # This question can't be answered from a single page: the model has
    # to first look at the front page of quotes.toscrape.com, notice
    # there's no obvious way to filter by tag from there, then decide to
    # browse the dedicated tag page directly, or page through results,
    # before it has enough to answer. That's exactly the kind of
    # multi-step research this loop is built for.
    question = (
        "On https://quotes.toscrape.com/, find two quotes tagged 'love' "
        "(hint: tag pages live at https://quotes.toscrape.com/tag/love/). "
        "Report each quote's text and its author."
    )

    print(f"Question: {question}\n")
    answer = run_agent(question)
    print("\nFinal answer:\n" + answer)


if __name__ == "__main__":
    main()
