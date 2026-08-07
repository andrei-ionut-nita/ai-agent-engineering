"""
Lesson 15: wrapping Playwright as a plain function, no AI involved yet.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/02_intermediate/15_wrapping_playwright_as_a_tool/lesson.py

Every lesson so far has been a standalone script: open a browser, do
one specific thing, close it, print the result. This lesson reshapes
that pattern into a single reusable function, browse(url), that takes
a URL in and returns readable page text out. That's deliberate: it's
the exact same idea as Lesson 13 of the langchain course, where a
calculator was written as a plain Python function before @tool ever
entered the picture. Get the function right first, on its own, before
handing it to a model in Lesson 16.
"""

from playwright.sync_api import sync_playwright


def browse(url: str) -> str:
    """Open a URL in a real browser and return its visible, readable text.

    This is intentionally plain Python: no decorator, no LLM, no
    knowledge that a model will ever call it. A good tool function
    should make sense and be testable entirely on its own, exactly like
    any other function you'd write and unit test.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # A real page can fail to load (typo'd URL, site down, no
        # internet). We catch that here and return a plain string
        # describing the failure, rather than letting an exception
        # crash the caller. That choice matters a lot once Lesson 16
        # hands this function to a model: a model can only react to text
        # it receives back, it can't catch a Python exception, so
        # failures need to come back as normal strings too.
        try:
            page.goto(url, timeout=15_000)
        except Exception as exc:  # noqa: BLE001 - deliberately broad, see above
            browser.close()
            return f"Could not load {url}: {exc}"

        # innerText (not innerHTML) returns only what a human would
        # actually see rendered on screen: no tags, no scripts, no CSS,
        # collapsed whitespace. That's exactly the shape of input a
        # language model wants, raw HTML would waste most of its
        # context window on markup it doesn't need.
        text = page.locator("body").inner_text()

        browser.close()

        # Real pages can be enormous. Trimming to a reasonable length
        # keeps this function's output small and predictable, which
        # will matter once it's feeding a model's limited context
        # window in Lesson 16.
        max_chars = 4000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...(truncated)"
        return text


def main() -> None:
    # Called directly, no AI, no decorator, just a function returning a
    # string. Lesson 16 will wrap this exact function with @tool and
    # hand it to a model, without changing a single line of its body.
    result = browse("https://quotes.toscrape.com/")
    print(result)

    print("\n---\n")

    # A deliberately broken URL, to show the error path returns a
    # string instead of raising.
    error_result = browse("https://this-domain-does-not-exist-12345.invalid/")
    print(error_result)


if __name__ == "__main__":
    main()
