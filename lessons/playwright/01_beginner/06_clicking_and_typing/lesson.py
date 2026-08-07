"""
Lesson 6: clicking and typing, actually interacting with a page.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/01_beginner/06_clicking_and_typing/lesson.py

Every lesson so far has only read from a page. This one changes that:
it fills in a login form on quotes.toscrape.com (a practice site that
accepts literally any username and password) and clicks submit,
exactly like a person would with a keyboard and mouse.
"""

from playwright.sync_api import sync_playwright

LOGIN_URL = "https://quotes.toscrape.com/login"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(LOGIN_URL)
        print("Loaded:", page.title())

        # .fill() clears whatever's in a text field, then sets its
        # value in one go. It's the normal choice for text inputs:
        # fast, and it fires the same events a real browser would
        # after typing, so the page's own JavaScript reacts correctly.
        page.locator("#username").fill("learner")

        # .type() is different: it sends one keystroke at a time,
        # simulating an actual person typing, including the small
        # delay between characters if you pass delay=. This is slower
        # than .fill(), and mostly needed for pages whose JavaScript
        # reacts to individual keystrokes, like a live search box or
        # a field with a character-by-character validator. For a
        # plain login field like this one, .fill() would work just as
        # well; .type() is used here so you've seen both.
        page.locator("#password").type("hunter2", delay=20)

        # .click() finds the element and clicks it, but not blindly:
        # Playwright first waits for the element to be visible,
        # attached to the page, and not covered by anything else,
        # This "auto-waiting" is covered properly in Lesson 9; for now
        # just know that .click() won't fire before the button is
        # actually ready to be clicked.
        page.locator("input[value='Login']").click()

        # Clicking submit triggers a real page navigation (the form
        # posts and the server sends back a new page), so we wait for
        # that new page to finish loading before reading anything
        # from it, the same idea from Lesson 4's page.goto().
        page.wait_for_load_state()

        print("URL after login:", page.url)

        # quotes.toscrape.com accepts any credentials and, once
        # "logged in", shows a "Logout" link that wasn't there before.
        # Checking for it confirms the click and form fill actually
        # worked, not just that no error was raised.
        logged_in = page.get_by_text("Logout").count() > 0
        print("Login appears successful:", logged_in)

        browser.close()


if __name__ == "__main__":
    main()
