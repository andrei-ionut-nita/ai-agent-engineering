"""
Lesson 20: multiple isolated browser contexts running at once.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/03_advanced/20_parallel_contexts/lesson.py

Lesson 18 showed one context's storage_state being reused by another.
This lesson shows the opposite: several contexts existing side by side,
from the same browser, that never share anything unless we explicitly
hand data between them ourselves.
"""

from concurrent.futures import ThreadPoolExecutor

from playwright.sync_api import sync_playwright

LOGIN_URL = "https://quotes.toscrape.com/login"


def log_in_as(username: str) -> dict:
    """Launch a fresh browser and context, log in with a distinct
    username, and report back what that context can see about itself.

    Playwright's sync API ties a Playwright instance and everything it
    creates (browser, context, page) to the thread that started it, it
    cannot be shared across threads. So instead of passing one shared
    browser into multiple threads, each thread runs this entire function
    independently, its own sync_playwright(), its own browser, its own
    context. That's still a fair demonstration of isolation: nothing
    here is shared between calls unless we explicitly return it."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Each call to browser.new_context() creates a completely
        # separate cookie jar and local storage, the same isolation a
        # normal browser gives you between two different profiles, or
        # two different incognito windows.
        context = browser.new_context()
        page = context.new_page()

        page.goto(LOGIN_URL)
        page.locator("#username").fill(username)
        page.locator("#password").fill("any-password-works")
        page.locator("input[type='submit']").click()
        page.wait_for_selector("a[href='/logout']")

        # Read back this context's own cookies, to prove later that no
        # two contexts ended up sharing a session by accident.
        cookies = context.cookies()
        session_cookie = next((c["value"] for c in cookies if c["name"] == "session"), None)

        context.close()
        browser.close()
        return {"username": username, "session_cookie": session_cookie}


def run_sequentially(usernames: list[str]) -> list[dict]:
    """The simplest version: one browser and context after another,
    still isolated, just not happening at the same time."""
    return [log_in_as(name) for name in usernames]


def run_concurrently(usernames: list[str]) -> list[dict]:
    """ThreadPoolExecutor gets us real concurrency: while one thread is
    waiting on a network response, another thread's page can make
    progress. Each thread runs log_in_as() with its own, fully separate
    Playwright instance, so there's no sharing to worry about."""
    with ThreadPoolExecutor(max_workers=len(usernames)) as pool:
        results = list(pool.map(log_in_as, usernames))
    return results


def main() -> None:
    usernames = ["alice", "bob", "carol"]

    print("=== Sequential contexts ===")
    sequential_results = run_sequentially(usernames)
    for result in sequential_results:
        print(f"  {result['username']}: session cookie = {result['session_cookie']}")

    print("\n=== Concurrent contexts (threads) ===")
    concurrent_results = run_concurrently(usernames)
    for result in concurrent_results:
        print(f"  {result['username']}: session cookie = {result['session_cookie']}")

    # Every session cookie should be different. If two contexts ever
    # shared state, we'd see duplicate values here, that's the whole
    # point of context isolation.
    all_cookies = [r["session_cookie"] for r in sequential_results + concurrent_results]
    print(f"\nAll {len(all_cookies)} session cookies unique: {len(set(all_cookies)) == len(all_cookies)}")


if __name__ == "__main__":
    main()
