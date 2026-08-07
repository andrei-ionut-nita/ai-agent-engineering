"""
Lesson 13: extracting structured data into typed Pydantic models.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/02_intermediate/13_extracting_structured_data/lesson.py

Earlier lessons pulled a single title or a single price off a page as
plain strings. Real scraping usually wants many records at once, each
with several fields, and each field with the right type (a price
should be a number you can do math on, not a string like "£51.77").
This lesson scrapes a whole page of books into a list of typed
Pydantic models.
"""

from playwright.sync_api import sync_playwright
from pydantic import BaseModel


class Book(BaseModel):
    """One book listing, with fields converted to their real types."""

    title: str
    price: float
    in_stock: bool
    rating: int


# Words on this site spell out star ratings instead of using digits, so
# we need a lookup table to convert "Three" into 3. This is a common
# real-world scraping problem: the data on the page is meant for
# humans to read, not for a program to parse directly, so some
# translation step is almost always necessary.
_RATING_WORDS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def scrape_books(url: str) -> list[Book]:
    books: list[Book] = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        # One locator, many matching elements: article.product_pod
        # matches every book card on the page at once. .all() turns that
        # into a plain Python list of individual locators, one per card,
        # so we can loop over them and pull each book's fields out
        # separately.
        for card in page.locator("article.product_pod").all():
            raw_title = card.locator("h3 a").get_attribute("title") or ""

            # Prices on this site look like "£51.77": a currency symbol
            # glued onto a number. [1:] slices off just the first
            # character (the £), leaving a string float() can parse.
            raw_price = card.locator(".price_color").text_content() or ""
            price = float(raw_price.strip()[1:])

            availability = card.locator(".availability").text_content() or ""
            in_stock = "In stock" in availability

            # The star rating is encoded as a CSS class, not visible
            # text, e.g. class="star-rating Three". get_attribute("class")
            # returns the whole class string; split() breaks it into
            # words, and the rating word is always the last one.
            rating_classes = card.locator("p.star-rating").get_attribute("class") or ""
            rating_word = rating_classes.split()[-1]
            rating = _RATING_WORDS.get(rating_word, 0)

            books.append(
                Book(
                    title=raw_title,
                    price=price,
                    in_stock=in_stock,
                    rating=rating,
                )
            )

        browser.close()

    return books


def main() -> None:
    books = scrape_books("https://books.toscrape.com/")

    print(f"Scraped {len(books)} books.\n")

    # Because each Book is a real Pydantic model, not a loose dictionary,
    # every book here is guaranteed to have a valid title (str), price
    # (float), in_stock (bool), and rating (int). If the page's HTML
    # ever changed in a way that broke our parsing, Pydantic would have
    # raised a validation error the moment we built the Book, instead of
    # letting bad data quietly flow downstream.
    for book in books[:5]:
        stars = "*" * book.rating
        stock_label = "in stock" if book.in_stock else "out of stock"
        print(f"  {book.title} - £{book.price:.2f} ({stock_label}, {stars})")

    average_price = sum(b.price for b in books) / len(books)
    print(f"\nAverage price across all {len(books)} books: £{average_price:.2f}")


if __name__ == "__main__":
    main()
