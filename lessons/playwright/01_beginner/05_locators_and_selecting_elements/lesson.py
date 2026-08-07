"""
Lesson 5: locators, Playwright's way of pointing at elements on a page.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/01_beginner/05_locators_and_selecting_elements/lesson.py

Lesson 4 loaded a page and read its title, one fixed, simple thing.
Real pages are made of many elements: book titles, prices, links,
buttons. This lesson introduces locators, the object you use to point
at one, or many, of those elements before doing anything with them.
"""

from playwright.sync_api import sync_playwright

URL = "https://books.toscrape.com/"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)

        # page.locator() takes a CSS selector, the same syntax used in
        # stylesheets, and returns a Locator: not the element itself,
        # but a reusable "recipe" for finding it. Nothing is looked up
        # yet, that only happens when you ask the locator to do
        # something, like .count() or .text_content().
        #
        # Every book on this page is wrapped in an <article
        # class="product_pod">, so this locator matches all of them.
        books = page.locator(".product_pod")
        print("Books found on this page:", books.count())

        # A locator matching multiple elements can be narrowed to one
        # with .first, .last, or .nth(index). .first is the first
        # matching element, the top-left book on this page.
        first_book = books.first

        # Locators can be chained: search inside the results of
        # another locator. Here we look for the <h3><a> title link,
        # but only within the first book, not the whole page.
        first_title = first_book.locator("h3 a")

        # Elements often carry more information in an attribute than
        # in their visible text. This site truncates long titles with
        # "..." in the visible text, but stores the full title in the
        # title="" attribute, so .get_attribute() reads that instead.
        print("First book title:", first_title.get_attribute("title"))

        # CSS selectors can combine a tag and a class, like a normal
        # stylesheet would: p.price_color means "a <p> with class
        # price_color".
        first_price = first_book.locator("p.price_color")
        print("First book price:", first_price.text_content())

        # get_by_text() is a different kind of locator entirely: it
        # searches by the visible text on the page instead of by CSS
        # structure. Useful when you know what a link or button says,
        # but not exactly where it sits in the HTML.
        next_link = page.get_by_text("next", exact=False)
        print("Found a 'next' link/button:", next_link.count() > 0)

        # get_by_role() is a third style, searching by accessibility
        # role, the same information a screen reader would use. It's
        # often the most robust choice, since it doesn't depend on
        # exact CSS classes or wording, only on what kind of element
        # something is and, optionally, its accessible name.
        all_links = page.get_by_role("link")
        print("Total links on the page:", all_links.count())

        browser.close()


if __name__ == "__main__":
    main()
