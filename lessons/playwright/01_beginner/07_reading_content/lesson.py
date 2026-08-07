"""
Lesson 7: reading real content off a page, structured, not just spot checks.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/01_beginner/07_reading_content/lesson.py

Earlier lessons read one thing at a time: a title, a price. This
lesson loops over every quote on quotes.toscrape.com and pulls out its
text, author, and tags into a plain Python list of dictionaries, the
shape of "scraped data" you'll actually want to work with afterward.
"""

from playwright.sync_api import sync_playwright

URL = "https://quotes.toscrape.com/"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)

        # Every quote on this page sits inside a <div class="quote">.
        # We loop over each one and pull three pieces out of it.
        quote_elements = page.locator(".quote")
        print("Quotes on this page:", quote_elements.count())

        quotes = []
        # .count() tells us how many matches there are; range(...)
        # then gives us each index in order, so .nth(i) can grab them
        # one at a time. This is the standard way to loop over a
        # Playwright locator that matches multiple elements.
        for i in range(quote_elements.count()):
            quote = quote_elements.nth(i)

            # .text_content() reads the element's visible text, with
            # any inner HTML tags stripped out. This is almost always
            # what you want when the goal is "the words a person would
            # read", as opposed to the markup around them.
            text = quote.locator(".text").text_content()
            author = quote.locator(".author").text_content()

            # .all_text_contents() is the plural form: instead of one
            # string, it returns a list of strings, one per matching
            # element. Here, each quote has several <a class="tag">
            # elements, and we want all of them, not just the first.
            tags = quote.locator(".tag").all_text_contents()

            quotes.append({"text": text, "author": author, "tags": tags})

        # .inner_html() is the other common read method: instead of
        # stripped visible text, it returns the raw HTML markup inside
        # the element. Rarely what you want for scraping data, but
        # useful for debugging (seeing exactly what structure you're
        # matching against) or when you deliberately need the markup,
        # e.g. to preserve bold/italic formatting.
        first_quote_html = quote_elements.first.locator(".text").inner_html()
        print("\nRaw HTML of the first quote's text:")
        print(f"  {first_quote_html[:70]}...")

        print(f"\nCollected {len(quotes)} quotes:")
        for q in quotes[:3]:
            print(f"  \"{q['text'][:40]}...\" - {q['author']} {q['tags']}")

        browser.close()


if __name__ == "__main__":
    main()
