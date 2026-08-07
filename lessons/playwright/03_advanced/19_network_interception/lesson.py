"""
Lesson 19: page.route(), mocking and blocking requests.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/03_advanced/19_network_interception/lesson.py

Every page load so far went straight to a real server and rendered
whatever came back. This lesson sits in between the page and the
network: intercepting requests before they leave the browser, and
deciding what happens to each one, serve a fake response, block it
outright, or let it through unchanged.
"""

import json

from playwright.sync_api import Route, sync_playwright


def mock_json_response(route: Route) -> None:
    """A route handler: instead of letting this request reach httpbin.org,
    answer it ourselves with made-up data."""
    fake_body = {
        "slideshow": {
            "author": "Not the real httpbin",
            "title": "Mocked entirely by Playwright",
        }
    }
    # route.fulfill() short-circuits the request: nothing is sent over the
    # network at all, the browser just receives this instead, as if it
    # came from the real server.
    route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(fake_body),
    )


def block_images(route: Route) -> None:
    """A route handler: refuse image requests outright."""
    # route.abort() is the opposite of fulfill(): the request never
    # completes at all, the browser sees it as a failed network request,
    # exactly like a real connection error.
    route.abort()


def demo_mocking_a_response() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # page.route(pattern, handler) tells Playwright: any request whose
        # URL matches this pattern should go through our handler function
        # first, instead of straight to the network. This has to be set
        # up before the matching request is made, which is why it comes
        # before page.goto().
        page.route("https://httpbin.org/json", mock_json_response)

        page.goto("https://httpbin.org/json")
        # This came from mock_json_response, not from httpbin.org. The
        # real endpoint returns a fixed sample JSON about a slideshow;
        # what actually rendered here is entirely made up by us.
        body_text = page.locator("body").text_content()
        print("Response body (should be our fake data):")
        print(body_text)

        browser.close()


def demo_blocking_requests() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # "**/*.jpg" and similar patterns use glob syntax: ** matches any
        # characters, including slashes. This matches any request URL
        # ending in a common image extension, across the whole page.
        page.route("**/*.{png,jpg,jpeg}", block_images)

        # Track which requests actually got aborted, so we can prove the
        # blocking really happened rather than just trusting the code.
        blocked_urls: list[str] = []
        page.on(
            "requestfailed",
            lambda request: blocked_urls.append(request.url),
        )

        page.goto("https://books.toscrape.com/")
        page.wait_for_load_state("networkidle")

        print(f"\nBlocked {len(blocked_urls)} image request(s).")
        if blocked_urls:
            print("First blocked URL:", blocked_urls[0])

        # The page still loaded, book titles and prices are plain text,
        # not images, so blocking images doesn't break the content we
        # actually care about scraping.
        first_title = page.locator("article.product_pod h3 a").first
        print("First book title still readable:", first_title.get_attribute("title"))

        browser.close()


def main() -> None:
    print("=== Mocking a response ===")
    demo_mocking_a_response()

    print("\n=== Blocking requests ===")
    demo_blocking_requests()


if __name__ == "__main__":
    main()
