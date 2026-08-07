"""
Lesson 18: logging in once, reusing storage_state across runs.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/03_advanced/18_authentication_and_storage_state/lesson.py

Every lesson so far started each browser context from a blank slate: no
cookies, no login, nothing remembered. Real agents that revisit the same
site over and over shouldn't have to log in every single time, this
lesson shows how to log in once, save that session to disk, and reuse it.
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

# storage_state gets written next to this lesson file, not to a system
# temp directory, so you can open it yourself afterward and see what's
# actually inside (spoiler: cookies and a bit of local storage, as JSON).
STATE_FILE = Path(__file__).parent / "auth_state.json"

LOGIN_URL = "https://quotes.toscrape.com/login"


def log_in_and_save_state() -> None:
    """Log in once with a fresh, blank context, then save its state to disk."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # A brand new context has no cookies at all, exactly like a
        # private/incognito window. This is intentional: we want to prove
        # the login below is what creates the session, not something left
        # over from a previous run.
        context = browser.new_context()
        page = context.new_page()

        page.goto(LOGIN_URL)
        # quotes.toscrape.com/login accepts ANY username and password, it
        # exists purely for practicing this exact workflow. A real site
        # would need real credentials, usually pulled from environment
        # variables, never hardcoded in a script like this.
        page.locator("#username").fill("student")
        page.locator("#password").fill("learning-playwright")
        page.locator("input[type='submit']").click()

        # After a successful login, the site shows a "Logout" link. This
        # is our proof the login actually worked before we bother saving
        # anything to disk.
        page.wait_for_selector("a[href='/logout']")
        print("Logged in successfully, 'Logout' link is visible.")

        # context.storage_state() captures every cookie and localStorage
        # entry the context is currently holding, and writes it out as
        # plain JSON. This is the entire "session", everything the site
        # needed to recognize us as logged in.
        context.storage_state(path=str(STATE_FILE))
        print(f"Saved session state to {STATE_FILE.name}")

        context.close()
        browser.close()


def reuse_saved_state() -> None:
    """Start a brand new context, but hand it the saved state up front."""
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # This is the key line: passing storage_state= to new_context()
        # pre-loads the cookies and local storage we saved earlier, before
        # the page ever loads. The browser believes it's already logged
        # in, because as far as cookies are concerned, it is.
        context = browser.new_context(storage_state=str(STATE_FILE))
        page = context.new_page()

        # Notice we go straight to the homepage, not /login, and never
        # fill in a username or password anywhere in this function.
        page.goto("https://quotes.toscrape.com/")

        logout_link = page.locator("a[href='/logout']")
        already_logged_in = logout_link.count() > 0
        print(f"Already authenticated on a fresh context: {already_logged_in}")

        context.close()
        browser.close()


def main() -> None:
    log_in_and_save_state()
    reuse_saved_state()

    # Clean up after ourselves so re-running this lesson always starts
    # from a real login, instead of silently reusing yesterday's file.
    if STATE_FILE.exists():
        STATE_FILE.unlink()
        print(f"Removed {STATE_FILE.name}")


if __name__ == "__main__":
    main()
