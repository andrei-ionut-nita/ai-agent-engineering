"""
Lesson 11: multi-page navigation, following links, and handling popups.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/02_intermediate/11_multi_page_navigation/lesson.py

So far every lesson has stayed on one page. Real browsing involves
following links to new pages, and sometimes those links open in a
brand new tab or popup window instead of replacing the current one.
This lesson covers both.
"""

from playwright.sync_api import sync_playwright


def follow_a_link_demo() -> tuple[str, str]:
    """Clicks a book title, which navigates the same page/tab to a new URL."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://books.toscrape.com/")

        start_url = page.url

        # Clicking a normal link navigates the SAME page object to a new
        # URL, it doesn't open anything new. page.locator(...).click()
        # already auto-waits for the resulting navigation to finish
        # before the next line runs, so page.url below reflects the new
        # page, not the old one.
        page.locator("article.product_pod h3 a").first.click()

        end_url = page.url
        browser.close()
        return start_url, end_url


def new_tab_demo() -> tuple[int, str]:
    """Handles a link that opens a second tab instead of navigating in place."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://the-internet.herokuapp.com/windows")

        # "Click Here" on this page opens a brand new tab via
        # target="_blank". If we just clicked it, `page` would still
        # point at the ORIGINAL tab, the new one would exist but we'd
        # have no reference to it. context.expect_page() solves this: it
        # starts listening for a new page/tab the moment it's entered,
        # so the one that opens inside this `with` block gets captured.
        with context.expect_page() as new_page_info:
            page.locator("a", has_text="Click Here").click()
        new_tab = new_page_info.value

        # A newly opened tab may still be loading; wait for it explicitly
        # before reading anything from it (see Lesson 9 on why we don't
        # just guess with a fixed sleep here).
        new_tab.wait_for_load_state()

        tab_count = len(context.pages)
        new_tab_text = new_tab.locator("h3").text_content() or ""

        browser.close()
        return tab_count, new_tab_text


def main() -> None:
    print("1. Following a link (same tab):")
    start, end = follow_a_link_demo()
    print(f"   Started at: {start}")
    print(f"   Ended at:   {end}")

    print("\n2. Handling a popup that opens a new tab:")
    count, text = new_tab_demo()
    print(f"   Tabs open in the context: {count}")
    print(f"   Text in the new tab: {text.strip()}")


if __name__ == "__main__":
    main()
