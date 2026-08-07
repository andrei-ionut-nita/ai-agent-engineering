"""
Lesson 3: launching a real, controllable browser.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/01_beginner/03_launching_a_browser/lesson.py

Lesson 2 made sure Chromium is actually downloaded. This lesson starts
it up for the first time, does almost nothing with it (that starts in
Lesson 4), and shuts it down cleanly. Everything else in this course
builds on the pattern shown here.
"""

from playwright.sync_api import sync_playwright


def main() -> None:
    # sync_playwright() starts Playwright's driver process and hands
    # us a "p" object we use to launch browsers. Using it as a
    # `with ... as p:` block (a "context manager") guarantees that
    # driver process is shut down cleanly when we're done, even if
    # something inside the block raises an error.
    with sync_playwright() as p:
        # p.chromium is Playwright's handle to the Chromium engine
        # installed in Lesson 2. .launch() actually starts a browser
        # process on this machine, the same kind of process your
        # everyday Chrome creates when you open it.
        #
        # headless=True (the default) means the browser runs with no
        # visible window, which is what you want on a server or in
        # CI. Setting headless=False pops open a real window you can
        # watch, useful while you're developing and want to see what
        # the browser is doing.
        browser = p.chromium.launch(headless=True)

        print("Browser launched.")
        print("Browser type:", browser.browser_type.name)
        print("Is connected:", browser.is_connected())

        # A "browser" on its own can't hold pages, it's the running
        # process. To actually visit anything, you need a "context"
        # (an isolated session, like a private browsing window, with
        # its own cookies and storage) and then a "page" inside it
        # (one browser tab). Contexts and pages are covered properly
        # starting next lesson, this is just enough to prove the
        # browser is alive.
        context = browser.new_context()
        page = context.new_page()
        print("Created one browser context and one page inside it.")

        # Always close what you opened, and close it in reverse order:
        # page, then context, then browser. Leaving a browser process
        # running in the background is the single most common mistake
        # when learning Playwright, it silently eats memory until you
        # notice your machine has a dozen headless Chromium processes
        # you forgot about.
        page.close()
        context.close()
        browser.close()
        print("Everything closed cleanly.")


if __name__ == "__main__":
    main()
