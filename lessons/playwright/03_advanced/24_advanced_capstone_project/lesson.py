"""
Lesson 24 (Capstone): an end-to-end web research agent.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/03_advanced/24_advanced_capstone_project/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root. This lesson
combines nearly everything the course covered: a browse(url) tool
(Lessons 15-16) wired to a Gemini model, restricted to a safe domain
allowlist (Lesson 23), with a real ask/run/respond loop (Lesson 14)
that lets the model decide, on its own, which pages to read before
answering a research question.
"""

from urllib.parse import urlparse

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from playwright.sync_api import sync_playwright

load_dotenv()

# The same safety principle from Lesson 23: never let an agent navigate
# anywhere it wants. Restricting to two known, stable practice sites
# keeps this capstone deterministic and safe to run unattended, exactly
# like an allowlist would in a production browsing agent.
ALLOWED_DOMAINS = {"books.toscrape.com", "quotes.toscrape.com"}

MAX_AGENT_TURNS = 6
MAX_PAGE_TEXT_CHARS = 4000


def _domain_is_allowed(url: str) -> bool:
    # urlparse breaks a URL into pieces; .netloc is the host part, e.g.
    # "books.toscrape.com" out of "https://books.toscrape.com/catalogue/".
    host = urlparse(url).netloc
    return host in ALLOWED_DOMAINS


@tool
def browse(url: str) -> str:
    """Fetch a page and return its visible text. Only works for URLs on
    books.toscrape.com or quotes.toscrape.com, any other domain is
    refused. Use full URLs, e.g. 'https://books.toscrape.com/'
    or 'https://quotes.toscrape.com/page/2/'."""
    if not _domain_is_allowed(url):
        # The model can only ask, it can't force this tool to run
        # (Lesson 14's "the AI decides, your code executes"). Returning a
        # clear refusal string, instead of raising, lets the model see
        # what happened and adjust, e.g. try a different, allowed URL.
        return f"Refused: {url!r} is outside the allowed domains {sorted(ALLOWED_DOMAINS)}."

    # A fresh, short-lived browser per call keeps this tool simple and
    # stateless, exactly what Lesson 15 aims for when first wrapping
    # Playwright as a plain function. A longer-running agent would
    # likely reuse one browser across calls instead, for speed.
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, timeout=15000)
        page.wait_for_load_state("networkidle")

        # Narrow, selector-restricted extraction, same principle Lesson
        # 23 taught: read what the page is actually built from, not a
        # blind dump of the entire document, since these practice sites
        # are trusted content this is mostly about keeping the text
        # focused and short, not about a hidden-injection risk here.
        text = page.locator("body").text_content() or ""
        browser.close()

    # Collapse repeated whitespace so the model isn't burning context
    # tokens on blank lines and indentation from the page's markup.
    cleaned = " ".join(text.split())
    return cleaned[:MAX_PAGE_TEXT_CHARS]


SYSTEM_PROMPT = """You are a careful web research assistant. You can \
only browse books.toscrape.com and quotes.toscrape.com, using the \
browse tool. Use it to look up real information before answering, \
don't guess. When you have enough information, answer the user's \
question directly and concisely, citing which page(s) you read from."""


def run_research_agent(model_with_tools, question: str) -> str:
    """The ask/run/respond loop from Lesson 14, extended into a real
    loop instead of three fixed steps: the model can call browse() as
    many times as it needs, deciding for itself when it has enough
    information to answer, up to a hard cap so a confused model can't
    loop forever."""
    messages: list = [SystemMessage(SYSTEM_PROMPT), HumanMessage(question)]

    for turn in range(1, MAX_AGENT_TURNS + 1):
        response: AIMessage = model_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            # No tool call means the model believes it already has
            # enough information, whatever it wrote is the final answer.
            return response.text

        for call in response.tool_calls:
            print(f"  [turn {turn}] browsing: {call['args'].get('url')}")
            result = browse.invoke(call["args"])
            messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

    return "Ran out of turns before reaching a final answer, try a narrower question."


def main() -> None:
    model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    model_with_tools = model.bind_tools([browse])

    questions = [
        "What is the cheapest book listed on the books.toscrape.com homepage?",
        "Who is quoted first on quotes.toscrape.com, and what is the quote?",
    ]

    for question in questions:
        print(f"\nQ: {question}")
        answer = run_research_agent(model_with_tools, question)
        print(f"A: {answer}")


if __name__ == "__main__":
    main()
