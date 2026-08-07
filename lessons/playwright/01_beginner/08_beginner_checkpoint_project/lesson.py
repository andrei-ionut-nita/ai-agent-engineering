"""
Lesson 8 (checkpoint): scrape a page's book titles and prices into a list.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/01_beginner/08_beginner_checkpoint_project/lesson.py

This lesson introduces nothing new. It's a checkpoint: everything from
Lessons 3 through 7, launching a browser, navigating to a page, using
locators, and reading content, combined into one small, real scraper
against books.toscrape.com. If any single line here is a surprise,
that's a sign to go back and reread the lesson it came from before
moving on to the intermediate tier.
"""

from playwright.sync_api import sync_playwright

URL = "https://books.toscrape.com/"


def scrape_books(url: str) -> list[dict]:
    """Return every book's title and price from one catalog page."""
    # This whole function is Lesson 3 (launch), Lesson 4 (navigate),
    # Lesson 5 (locate), and Lesson 7 (read), each doing exactly the
    # job it did in its own lesson, just now working together.
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # Two parallel locators: one for every title link, one for
        # every price, both scoped under the same .product_pod
        # structure used in Lesson 5. Because both locators walk the
        # page in the same top-to-bottom order, index i in one lines
        # up with index i in the other, book number i's title matches
        # book number i's price.
        titles = page.locator(".product_pod h3 a")
        prices = page.locator(".product_pod p.price_color")

        count = titles.count()
        books = []
        for i in range(count):
            # .get_attribute("title") over .text_content(): this site
            # truncates long titles with "..." in the visible text,
            # but the full title lives in the title="" attribute, the
            # same trick from Lesson 5.
            title = titles.nth(i).get_attribute("title")
            price = prices.nth(i).text_content()
            books.append({"title": title, "price": price})

        browser.close()
        return books


def main() -> None:
    books = scrape_books(URL)

    print(f"Scraped {len(books)} books from {URL}\n")
    for book in books:
        print(f"  {book['price']:>8}  {book['title']}")


if __name__ == "__main__":
    main()
