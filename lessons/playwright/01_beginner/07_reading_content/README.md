# Lesson 7: Reading content off a page

## From one thing to many things

Lessons 4 and 5 read one value at a time: a title, a price. Real
scraping usually means the opposite: loop over every matching element
on a page and pull structured data out of each one. This lesson does
exactly that against quotes.toscrape.com, ten quotes on the page, each
with a text, an author, and a list of tags, collected into a plain
Python list of dictionaries.

That list-of-dictionaries shape is deliberate. It's the same shape
you'd get back from a database query or a JSON API, which makes it
easy to save, filter, or hand off to something else later, exactly the
shape Lesson 13, extracting structured data into typed Pydantic
models, builds on.

## `.text_content()` versus `.inner_html()`

Two different ways to read what's inside an element, and they answer
different questions:

- **`.text_content()`** returns the visible text, with any HTML tags
  stripped out. If an element contains `<span>Hello <b>world</b></span>`,
  this returns `"Hello world"`. This is almost always what you want
  when scraping data meant to be read, prices, names, quotes.
- **`.inner_html()`** returns the raw markup inside the element,
  `"Hello <b>world</b>"` in the example above. Less commonly what you
  want for data extraction, but genuinely useful for two things:
  debugging (seeing exactly what structure you're matching against,
  when a selector isn't behaving the way you expected) and cases where
  you deliberately need to preserve formatting rather than strip it.

## Looping over multiple matches

A locator that matches several elements doesn't behave like a Python
list you can directly iterate with `for x in locator`. Instead, the
standard pattern is: get the count, then index into the locator with
`.nth(i)` for each position.

```python
for i in range(quote_elements.count()):
    quote = quote_elements.nth(i)
```

`range(quote_elements.count())` produces `0, 1, 2, ...` up to (but not
including) the count, one index for each match, which `.nth(i)` then
uses to grab that specific element.

## The plural read: `.all_text_contents()`

Where `.text_content()` reads one element's text, `.all_text_contents()`
reads every matching element's text at once and returns them as a
list of strings. Here, each quote has multiple `<a class="tag">`
elements underneath it, and the goal is all of them, not just the
first, so `.all_text_contents()` is the natural fit, no manual loop
needed.

## The code, piece by piece

```python
quote_elements = page.locator(".quote")
```

One locator, matching all ten `<div class="quote">` blocks on the
page.

```python
for i in range(quote_elements.count()):
    quote = quote_elements.nth(i)
    text = quote.locator(".text").text_content()
    author = quote.locator(".author").text_content()
    tags = quote.locator(".tag").all_text_contents()
    quotes.append({"text": text, "author": author, "tags": tags})
```

For each quote, narrow to that one element, then read three things out
of it: the quote text, the author's name, and every tag, into one
dictionary appended to a growing list.

```python
first_quote_html = quote_elements.first.locator(".text").inner_html()
```

The raw markup version of the first quote's text, shown purely so you
can compare it against the stripped `.text_content()` version above.

## Running it

```bash
uv run python lessons/playwright/01_beginner/07_reading_content/lesson.py
```

## Expected output

```
Quotes on this page: 10

Raw HTML of the first quote's text:
  "The world as we have created it is a process of our thinking. It cann...

Collected 10 quotes:
  ""The world as we have created it is a pr..." - Albert Einstein ['change', 'deep-thoughts', 'thinking', 'world']
  ""It is our choices, Harry, that show wha..." - J.K. Rowling ['abilities', 'choices']
  ""There are only two ways to live your li..." - Albert Einstein ['inspirational', 'life', 'live', 'miracle', 'miracles']
```

(The actual quote marks are curly quotation characters, they may
render slightly differently depending on your terminal's font.)

## Checkpoint

- **`.text_content()`**: visible text with HTML tags stripped, the
  usual choice for extracting readable data.
- **`.inner_html()`**: raw markup, useful for debugging selectors or
  preserving formatting, rarely what you want for plain data.
- **Looping a multi-match locator**: `for i in
  range(locator.count()): locator.nth(i)`, since a locator isn't
  directly iterable like a Python list.
- **`.all_text_contents()`**: the plural read, all matching elements'
  text as a list of strings, in one call.
- **List of dictionaries**: the shape scraped data usually ends up
  in, easy to save, filter, or pass along to something else.

If anything here still feels unclear, ask before moving to Lesson 8.
