# Lesson 13: Extracting structured data

## From loose strings to real types

Reading `.text_content()` off an element always gives you back a
plain string, even when the thing on the page is really a number, a
yes/no flag, or a date. `"£51.77"` is a string. `"In stock (22
available)"` is a string. If you want to compute an average price, or
filter to only in-stock items, you first need to turn those strings
into an actual `float` and `bool`. Doing that conversion by hand, over
and over, invites bugs (a stray currency symbol breaks `float()`, a
typo in a comparison silently returns the wrong books).

This is exactly what Pydantic's `BaseModel` is for: define the shape
of one record once, with real types, and let Pydantic enforce it every
time you build one. If the data doesn't fit the shape, you get a loud
error immediately, not a corrupted value three steps later.

## The code, piece by piece

```python
class Book(BaseModel):
    title: str
    price: float
    in_stock: bool
    rating: int
```

This is the whole schema: four fields, each with a real Python type.
Every `Book` object this lesson creates is guaranteed to actually have
these fields, with these types, or Pydantic raises a validation error
the moment you try to build it.

```python
for card in page.locator("article.product_pod").all():
```

`page.locator(...)` can match many elements at once (every book card
on the page); `.all()` turns that into a plain Python list you can loop
over, one locator per card, so each iteration deals with a single
book's fields in isolation.

```python
raw_price = card.locator(".price_color").text_content() or ""
price = float(raw_price.strip()[1:])
```

The page shows prices like `"£51.77"`, a currency symbol glued onto a
number, meant for a human eye, not a parser. `[1:]` is Python slice
syntax meaning "everything from index 1 onward," which drops just the
first character (the `£`), leaving `"51.77"` for `float()` to parse.

```python
rating_classes = card.locator("p.star-rating").get_attribute("class") or ""
rating_word = rating_classes.split()[-1]
rating = _RATING_WORDS.get(rating_word, 0)
```

The star rating isn't in any visible text at all, it's encoded in a
CSS class name, like `class="star-rating Three"`. `get_attribute` reads
the raw attribute string, `.split()` breaks it into words on
whitespace, and `[-1]` (the last item) is always the rating word. A
small lookup dictionary (`_RATING_WORDS`) converts that word into the
integer we actually want. This is a very normal shape for real-world
scraping: the data you need is on the page, just not in the format you
need it in, and some translation step almost always sits between "what
the page shows" and "what your program needs."

```python
books.append(Book(title=raw_title, price=price, in_stock=in_stock, rating=rating))
```

Only once every field has been converted to its real type do we build
the `Book`. If, say, `price` still held a string here, Pydantic would
raise a clear `ValidationError` immediately, catching the mistake right
at the source instead of letting a broken value travel through the
rest of the program.

## Running it

```bash
uv run python lessons/playwright/02_intermediate/13_extracting_structured_data/lesson.py
```

## Expected output

```
Scraped 20 books.

  A Light in the Attic - £51.77 (in stock, ***)
  Tipping the Velvet - £53.74 (in stock, *)
  Soumission - £50.10 (in stock, *)
  Sharp Objects - £47.82 (in stock, ****)
  Sapiens: A Brief History of Humankind - £54.23 (in stock, *****)

Average price across all 20 books: £38.05
```

Exact prices may shift slightly if the practice site's sample data
changes, the structure and types will not.

## Checkpoint

- **`BaseModel`**: defines a schema, field names plus real Python
  types, that Pydantic enforces every time you build one.
- **Why not just use dictionaries**: a dictionary has no guaranteed
  shape, a typo'd key or wrong type fails silently; a `BaseModel`
  fails loudly, immediately, at the point of construction.
- **`.locator(...).all()`**: turns a multi-element locator into a
  plain Python list, one locator per match, so you can loop over
  records individually.
- **Translating page data to real types**: prices, ratings, and flags
  on a page are formatted for humans, not parsers; expect a small
  conversion step (slicing, lookup tables) between raw text and the
  type your model actually needs.

If anything here still feels unclear, ask before moving to Lesson 14.
