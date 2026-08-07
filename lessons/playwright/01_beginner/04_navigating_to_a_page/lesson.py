"""
Lesson 4: navigating to a real page and waiting for it to load.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/01_beginner/04_navigating_to_a_page/lesson.py

Lesson 3 launched a browser and opened one empty tab, "about:blank".
This lesson finally sends that tab somewhere real: books.toscrape.com,
a site built specifically for practicing scraping, and reads back a
few basic facts once the page has actually finished loading.
"""

from playwright.sync_api import sync_playwright

URL = "https://books.toscrape.com/"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # page.goto() does two things: it tells the browser to start
        # loading the URL, and by default it waits for the "load"
        # event before returning control to your code, meaning the
        # page's main resources (HTML, CSS, images) have finished
        # loading. That wait is what makes the next line safe to run
        # immediately, there's no race between "did the page load yet"
        # and "read something off it".
        response = page.goto(URL)

        # goto() returns a Response object describing what the server
        # sent back, useful for confirming the request actually
        # succeeded before trying to read anything from the page.
        print("Navigated to:", page.url)
        print("HTTP status:", response.status if response else "no response")

        # page.title() reads the <title> tag, one of the simplest
        # possible things to pull off a loaded page, and a good first
        # sanity check that you landed somewhere real.
        print("Page title:", page.title())

        # wait_for_load_state() can be called again on its own, useful
        # when a page keeps loading things (like images) after the
        # initial "load" event goto() already waited for. "networkidle"
        # waits until there have been no new network requests for a
        # short while, a stronger, slower guarantee than the default.
        # We call it here just to demonstrate it exists; the default
        # wait from goto() was already enough for this simple page.
        page.wait_for_load_state("networkidle")
        print("Confirmed the network has gone idle, page is fully settled.")

        browser.close()


if __name__ == "__main__":
    main()
