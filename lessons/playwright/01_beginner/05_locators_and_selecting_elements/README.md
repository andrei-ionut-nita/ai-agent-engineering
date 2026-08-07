# Lesson 5: Locators and selecting elements

## A locator is a recipe, not a result

`page.locator(".product_pod")` does not go find anything on the page
the moment you call it. It builds a `Locator` object: a saved
description of what to look for, CSS selector, text, or role, that
gets re-run every time you actually ask it to do something, like
`.count()`, `.text_content()`, or (starting next lesson) `.click()`.

This matters more than it sounds like it should. Because a locator
re-runs its search each time, it stays correct even if the page
changes in between, an item gets added, a list re-renders after a
click. You're not holding a snapshot of "the element as it was", you're
holding a live pointer to "whatever currently matches this
description." That's a deliberate design choice, and it's a big part
of why Playwright scripts are less flaky than older tools that grab a
reference once and hope the page doesn't change.

## Three ways to point at something

This lesson shows three different selector styles, because each one
fits a different situation:

- **CSS selectors**, via `page.locator(".product_pod")`: the same
  syntax you'd use in a stylesheet, matching by tag, class, or id.
  Precise and fast, but brittle if a site's CSS classes change.
- **Text**, via `page.get_by_text("next")`: matches by what's visibly
  written on the page. Great when you know the wording but not the
  underlying HTML structure.
- **Role**, via `page.get_by_role("link")`: matches by accessibility
  role, the same category a screen reader would announce (link,
  button, heading, and so on). Often the most durable choice, and the
  one Playwright's own documentation recommends reaching for first,
  because it describes what something is, not how it happens to be
  styled or worded right now.

There's no single right answer for every situation, this course uses
whichever fits the page being scraped, and later lessons keep
reinforcing all three.

## Narrowing and chaining

A locator that matches many elements, `.product_pod` matches all 20
books on this page, can be narrowed down. `.first` and `.last` grab
the first or last match, `.nth(2)` grabs a specific index (zero-based,
so `.nth(0)` is the same as `.first`). Locators can also be chained:
calling `.locator(...)` on a locator searches only inside its
matches, not the whole page, which is how `first_book.locator("h3
a")` finds the title link belonging to just that one book, not all 20.

## The code, piece by piece

```python
books = page.locator(".product_pod")
print("Books found on this page:", books.count())
```

Every book on this page sits inside an `<article
class="product_pod">`. `.count()` runs the search and reports how many
matched.

```python
first_book = books.first
first_title = first_book.locator("h3 a")
print("First book title:", first_title.get_attribute("title"))
```

Narrow to one book, then search inside just that book for its title
link. This site visually truncates long titles with "...", but stores
the untruncated version in the link's `title=""` attribute, so reading
the attribute (not the visible text) gets the real, full title.

```python
next_link = page.get_by_text("next", exact=False)
```

`exact=False` (the default) means "contains this text", not "matches
it exactly", which matters since the actual link text might have
surrounding whitespace or capitalization you don't want to have to
match precisely.

```python
all_links = page.get_by_role("link")
print("Total links on the page:", all_links.count())
```

Every element the browser's accessibility tree considers a link,
regardless of its CSS class or exact markup.

## Running it

```bash
uv run python lessons/playwright/01_beginner/05_locators_and_selecting_elements/lesson.py
```

## Expected output

```
Books found on this page: 20
First book title: A Light in the Attic
First book price: £51.77
Found a 'next' link/button: True
Total links on the page: 94
```

## Checkpoint

- **Locator**: a reusable, live pointer to whatever currently matches
  a description, not a one-time snapshot.
- **CSS selectors**: precise structural matching, via
  `page.locator(".class")`, the same syntax as a stylesheet.
- **Text selectors**: `page.get_by_text(...)`, matches by what's
  visibly written on the page.
- **Role selectors**: `page.get_by_role(...)`, matches by
  accessibility role, often the most durable choice.
- **Narrowing and chaining**: `.first`, `.last`, `.nth(i)` narrow a
  multi-match locator; calling `.locator()` on a locator searches only
  within its matches.

If anything here still feels unclear, ask before moving to Lesson 6.
