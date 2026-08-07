"""
Lesson 9: waiting strategies, and why fixed sleeps make scripts flaky.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/02_intermediate/09_waiting_strategies/lesson.py

The beginner tier clicked and read elements that were already on the
page the moment it loaded. Real pages are rarely that polite: content
shows up late, after a network request or a bit of JavaScript finishes
running. This lesson is about waiting for that content correctly,
instead of guessing how long it will take.
"""

import time

from playwright.sync_api import sync_playwright


def the_wrong_way(url: str) -> None:
    """Demonstrates the anti-pattern: a fixed sleep instead of a real wait."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        # time.sleep() just pauses the whole script for a fixed number of
        # seconds, no matter what the page is actually doing. Too short
        # and the element isn't there yet, so the next line crashes. Too
        # long and every run of your script wastes time waiting on a page
        # that was already ready. Neither number is ever really correct,
        # because "how long the page takes" isn't a constant, it depends
        # on network speed, server load, and your own machine that day.
        time.sleep(2)
        print("Slept blindly for 2 seconds, hoping the page was ready.")

        browser.close()


def the_right_way(url: str) -> None:
    """Demonstrates waiting for a specific condition instead of a fixed time."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        # wait_for_selector blocks only until this exact element shows up
        # in the page (or raises an error if it never does, by default
        # after 30 seconds). That's the key difference from time.sleep:
        # it waits exactly as long as needed, no more, no less.
        page.wait_for_selector("article.product_pod")
        print("Waited for the actual product listing to appear.")

        browser.close()


def auto_wait_in_action(url: str) -> str:
    """Shows that locator actions already wait for you, most of the time."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        # This is the part beginners usually don't realize: you were
        # already using Playwright's waiting system in earlier lessons,
        # even without calling wait_for_selector yourself. A locator's
        # .click(), .fill(), and .text_content() all auto-wait: before
        # acting, Playwright checks that the element exists, is visible,
        # and isn't covered by anything else, retrying for a few seconds
        # if not. This is called "actionability", and it's why most
        # Playwright scripts never need an explicit wait at all.
        first_title = page.locator("article.product_pod h3 a").first
        title = first_title.get_attribute("title")

        browser.close()
        return title or ""


def wait_for_load_state_demo(url: str) -> None:
    """Shows waiting for the network to settle, useful after a click."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        # "networkidle" waits until there have been no new network
        # requests for a short stretch of time. It's a blunter tool than
        # wait_for_selector: useful when you don't know the exact
        # element to wait for, but slower and less precise, since a page
        # can sit there polling something in the background forever and
        # never truly go idle. Prefer wait_for_selector when you can name
        # the element you actually need.
        page.wait_for_load_state("networkidle")
        print("Network went idle, page is fully settled.")

        browser.close()


def main() -> None:
    url = "https://books.toscrape.com/"

    print("1. The wrong way: a fixed sleep.")
    the_wrong_way(url)

    print("\n2. The right way: wait_for_selector.")
    the_right_way(url)

    print("\n3. Auto-wait: locator actions wait for you automatically.")
    title = auto_wait_in_action(url)
    print(f"   First book title: {title}")

    print("\n4. wait_for_load_state: waiting on the network instead of an element.")
    wait_for_load_state_demo(url)


if __name__ == "__main__":
    main()
