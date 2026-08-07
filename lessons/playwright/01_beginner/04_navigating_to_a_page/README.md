# Lesson 4: Navigating to a page

## A shortcut: `browser.new_page()`

Lesson 3 was explicit: `browser.new_context()`, then
`context.new_page()`. That's the "correct" long form, and you'll use
it directly again starting in Lesson 20, when running multiple
isolated sessions at once actually matters. For a single page, though,
Playwright offers a shortcut, `browser.new_page()`, which creates a
default context behind the scenes and returns a page from it directly.
This lesson uses that shortcut, and so will most of the rest of this
course, since one browser and one page is the common case.

## What `page.goto()` actually waits for

Calling `page.goto(url)` doesn't just fire off a request and return
immediately. By default, it waits until the browser's "load" event
fires, meaning the page's HTML, CSS, and other core resources have
finished loading, before handing control back to your code. That's
the reason you can call `page.title()` on the very next line without
worrying about a race between "is the page there yet" and "read
something from it": Playwright already waited for you.

This default wait is good enough for most pages, including the ones
this course uses. Some pages, especially ones that keep fetching data
in the background after the initial load (a chat app, an infinite
scroll feed), need a stronger guarantee. `page.wait_for_load_state(
"networkidle")` waits until there's been no network activity for a
short stretch of time, a heavier, slower check than the default.
Lesson 9 covers waiting strategies properly, this lesson just shows
that the tool exists.

## Checking the response

`page.goto()` returns a `Response` object (or `None` in rare edge
cases), the same kind of response you'd get from any HTTP request:
a status code, headers, and so on. Checking `response.status` is a
cheap way to confirm the navigation actually succeeded (`200`) rather
than silently landing on an error page (`404`, `500`).

## The code, piece by piece

```python
response = page.goto(URL)
```

Navigates the page and waits for the load event. `response` holds
the server's reply.

```python
print("HTTP status:", response.status if response else "no response")
```

A conditional expression (`value_if_true if condition else
value_if_false`), Python's compact form of an if/else that produces a
value rather than running a statement. Here it guards against the
rare case where `goto()` returns `None`.

```python
print("Page title:", page.title())
```

Reads the page's `<title>` tag directly from the live, loaded DOM,
not from the raw HTML text, an important distinction once pages start
changing their own content with JavaScript after loading.

```python
page.wait_for_load_state("networkidle")
```

An extra, stronger wait, on top of the one `goto()` already did. Not
needed for this particular page, shown here so you recognize it later
when a trickier page needs it.

## Running it

```bash
uv run python lessons/playwright/01_beginner/04_navigating_to_a_page/lesson.py
```

## Expected output

```
Navigated to: https://books.toscrape.com/
HTTP status: 200
Page title: All products | Books to Scrape - Sandbox
Confirmed the network has gone idle, page is fully settled.
```

## Checkpoint

- **`browser.new_page()`**: a shortcut that creates a default context
  and one page in it, used when you don't need multiple isolated
  sessions.
- **`page.goto(url)`**: navigates and, by default, waits for the
  page's core resources to finish loading before returning.
- **`response.status`**: the HTTP status code, a quick way to confirm
  navigation actually succeeded.
- **`page.wait_for_load_state("networkidle")`**: a stronger, slower
  wait for pages that keep loading things after the initial load.

If anything here still feels unclear, ask before moving to Lesson 5.
