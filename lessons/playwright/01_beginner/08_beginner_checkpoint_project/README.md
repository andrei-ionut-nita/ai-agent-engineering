# Lesson 8: Beginner checkpoint, scrape a page into a list

## What this checkpoint is for

This lesson doesn't teach a new Playwright concept. It's a checkpoint:
a small, real script that puts Lessons 3 through 7 to work together in
one place. If you can read `lesson.py` top to bottom and predict what
each line does before reading its comment, the beginner tier has
landed. If any line surprises you, that's useful information, go back
to the lesson it came from (noted below) before starting the
intermediate tier.

| Line in this lesson | Comes from |
|---|---|
| `with sync_playwright() as p: ... p.chromium.launch()` | Lesson 3, launching a browser |
| `page.goto(url)` | Lesson 4, navigating to a page |
| `page.locator(".product_pod h3 a")` | Lesson 5, locators and selectors |
| `.get_attribute("title")`, `.text_content()`, looping with `.nth(i)` | Lesson 7, reading content |

Lesson 6 (clicking and typing) isn't exercised here, this particular
scrape doesn't need to interact with anything, just read what's
already on the page. It'll come back starting in Lesson 10.

## The task

Scrape every book on the books.toscrape.com front page into a Python
list of dictionaries, each with a `title` and a `price`. This is
exactly the shape of a real, small scraping job: load a catalog page,
pull structured data off it, and end up with something you could save
to a CSV, insert into a database, or hand to an LLM.

## The code, piece by piece

```python
def scrape_books(url: str) -> list[dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
```

The function is given a URL rather than hardcoding it inside, a small
habit worth building early: it makes the function reusable and, later,
easy to wrap as a tool (Lesson 15) without rewriting anything inside
it.

```python
        titles = page.locator(".product_pod h3 a")
        prices = page.locator(".product_pod p.price_color")
```

Two locators built from the same underlying structure, one for the
title link inside each book, one for its price. Because both locators
walk the page top to bottom, matching in the same order, index `i` in
`titles` always corresponds to the same book as index `i` in `prices`.

```python
        count = titles.count()
        books = []
        for i in range(count):
            title = titles.nth(i).get_attribute("title")
            price = prices.nth(i).text_content()
            books.append({"title": title, "price": price})
```

The Lesson 7 pattern: count the matches, loop by index, narrow each
locator to one element with `.nth(i)`, read what you need, and append
a dictionary to a growing list. `.get_attribute("title")` is used
instead of `.text_content()` for the title specifically because this
site truncates long titles visually but keeps the full text in the
`title=""` attribute, the same trick from Lesson 5.

```python
        browser.close()
        return books
```

Close the browser before returning, the function is responsible for
cleaning up everything it opened, exactly like every earlier lesson's
`with` block did.

## Running it

```bash
uv run python lessons/playwright/01_beginner/08_beginner_checkpoint_project/lesson.py
```

## Expected output

```
Scraped 20 books from https://books.toscrape.com/

   £51.77  A Light in the Attic
   £53.74  Tipping the Velvet
   £50.10  Soumission
   £47.82  Sharp Objects
   £54.23  Sapiens: A Brief History of Humankind
   £22.65  The Requiem Red
   £33.34  The Dirty Little Secrets of Getting Your Dream Job
   £17.93  The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull
   ...
```

(Twenty books total; exact prices are stable on this practice site,
but if the site's content ever changes, that's fine, the shape of the
output, a list of title/price pairs, is what matters here.)

## Checkpoint

- **This lesson introduced nothing new**: it's Lessons 3 to 7 working
  together, launch, navigate, locate, read.
- **Parallel locators, matched by index**: two locators built from the
  same page structure stay aligned, `.nth(i)` in one corresponds to
  `.nth(i)` in the other.
- **Function boundaries**: taking `url` as a parameter, opening and
  closing the browser inside the function, and returning plain data
  (a list of dictionaries) rather than printing from inside it, is the
  shape Lesson 15 builds on when this kind of function becomes an
  agent tool.
- **If something here didn't make sense**: reread the specific earlier
  lesson listed in the table above before starting the intermediate
  tier.

If anything here still feels unclear, ask before moving to Lesson 9.
