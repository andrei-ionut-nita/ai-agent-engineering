"""
Lesson 21: resilience patterns for real, unpredictable sites.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/03_advanced/21_retries_and_flaky_pages/lesson.py

Lesson 09 covered Playwright's built-in auto-waiting, which handles the
common case of "this element isn't ready yet". This lesson is about the
next layer up: real websites sometimes fail outright, a slow server, a
dropped connection, a page that occasionally doesn't finish loading. The
fix isn't a longer timeout, it's retrying the whole operation.
"""

import time
from typing import Callable, TypeVar

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

T = TypeVar("T")

DYNAMIC_LOADING_URL = "https://the-internet.herokuapp.com/dynamic_loading/1"


def retry_with_backoff(
    operation: Callable[[int], T],
    attempts: int = 4,
    initial_delay_seconds: float = 1.0,
) -> T:
    """Run operation(attempt_number), retrying with an increasing delay
    between tries if it raises a timeout.

    "Backoff" means each retry waits longer than the last, instead of
    hammering a struggling server at a fixed interval, which tends to
    make things worse, not better. This doubles the delay each time
    (1s, then 2s, then 4s, ...), a common pattern called exponential
    backoff. The attempt number is handed to operation() so it can also
    grow more patient on each retry, not just wait longer between them.
    """
    delay = initial_delay_seconds
    last_error: Exception | None = None

    for attempt_number in range(1, attempts + 1):
        try:
            return operation(attempt_number)
        except PlaywrightTimeoutError as exc:
            last_error = exc
            print(f"  Attempt {attempt_number}/{attempts} failed: {exc.message.splitlines()[0]}")
            if attempt_number < attempts:
                print(f"  Waiting {delay:.1f}s before retrying...")
                time.sleep(delay)
                delay *= 2

    # If every attempt failed, raise the last real error rather than
    # swallowing it silently, a caller needs to know retries didn't help.
    assert last_error is not None
    raise last_error


def load_dynamic_content(page: Page, attempt_number: int) -> str:
    """One attempt at the flaky operation: load a page where content is
    injected after a delay, and wait for it to show up.

    the-internet.herokuapp.com/dynamic_loading/1 hides an element until
    a "Start" button is clicked, then reveals it a few seconds later,
    a fixed delay meant to stand in for a real server that's sometimes
    slow. We deliberately start with a tight timeout that's shorter
    than the real delay, and grow it on each retry, which mirrors a
    common real pattern: give a shaky operation more patience each
    time, instead of giving up after one strict attempt.
    """
    page.goto(DYNAMIC_LOADING_URL)
    page.locator("#start button").click()

    # Milliseconds. Attempt 1 is deliberately too short to succeed, on
    # purpose, so this lesson has a real failure to recover from instead
    # of a contrived one.
    timeout_ms = 1500 * (2 ** (attempt_number - 1))
    page.locator("#finish").wait_for(state="visible", timeout=timeout_ms)
    return page.locator("#finish").text_content() or ""


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        print("Loading dynamic content with retry + backoff:")
        try:
            text = retry_with_backoff(lambda attempt: load_dynamic_content(page, attempt), attempts=4)
            print(f"\nSucceeded: {text!r}")
        except PlaywrightTimeoutError:
            print("\nGave up after all retries, this page may just be having a bad day.")

        browser.close()


if __name__ == "__main__":
    main()
