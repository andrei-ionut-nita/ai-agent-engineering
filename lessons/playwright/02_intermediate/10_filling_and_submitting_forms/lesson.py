"""
Lesson 10: filling and submitting forms.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/02_intermediate/10_filling_and_submitting_forms/lesson.py

Lesson 6 (beginner tier) covered .fill() and .click() on a single field.
This lesson puts those together into an actual form: text fields,
a checkbox, a dropdown, and a submit button, then confirms the result.
"""

from playwright.sync_api import sync_playwright


def login_form_demo() -> bool:
    """Fills in and submits a login form, then checks whether it worked."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://quotes.toscrape.com/login")

        # This practice site accepts any username and password, it's not
        # checking credentials for real, it just wants both fields
        # non-empty. .fill() clears whatever was in the field first, then
        # types the given text, which is why it's the right choice here
        # instead of .type() (which appends to whatever's already there).
        page.locator("#username").fill("agent-student")
        page.locator("#password").fill("does-not-matter")

        # Submitting a form is just clicking its submit button. Playwright
        # doesn't need a separate "submit" concept, a normal .click() on
        # a button with type="submit" does exactly what a real user
        # clicking it would do.
        page.locator("input[type='submit']").click()

        # After a successful login, this site shows a "Logout" link that
        # wasn't there before. Checking for it is how we confirm the
        # form submission actually worked, rather than just hoping.
        logged_in = page.locator("a[href='/logout']").is_visible()

        browser.close()
        return logged_in


def checkbox_demo() -> tuple[bool, bool]:
    """Toggles checkboxes on the-internet's dedicated checkboxes page."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://the-internet.herokuapp.com/checkboxes")

        checkboxes = page.locator("#checkboxes input[type='checkbox']")

        # .check() and .uncheck() are idempotent: calling .check() on a
        # box that's already checked does nothing (no error), unlike
        # .click(), which would toggle it off. Use .check()/.uncheck()
        # whenever you want a specific end state, not just "click it."
        checkboxes.nth(0).check()
        checkboxes.nth(1).uncheck()

        first_checked = checkboxes.nth(0).is_checked()
        second_checked = checkboxes.nth(1).is_checked()

        browser.close()
        return first_checked, second_checked


def dropdown_demo() -> str:
    """Selects an option from a <select> dropdown."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://the-internet.herokuapp.com/dropdown")

        dropdown = page.locator("#dropdown")

        # select_option() targets a real HTML <select> element. You can
        # pick by the option's value attribute, its visible label, or its
        # position, here we pick by label since that's what a human would
        # actually read on screen.
        dropdown.select_option(label="Option 2")

        selected_label = dropdown.locator("option:checked").text_content()

        browser.close()
        return selected_label or ""


def main() -> None:
    print("1. Login form (text fields + submit):")
    success = login_form_demo()
    print(f"   Logged in successfully: {success}")

    print("\n2. Checkboxes:")
    first, second = checkbox_demo()
    print(f"   Checkbox 1 checked: {first}, checkbox 2 checked: {second}")

    print("\n3. Dropdown:")
    label = dropdown_demo()
    print(f"   Selected option: {label}")


if __name__ == "__main__":
    main()
