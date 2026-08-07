# Lesson 11: Multi-page navigation

## Two very different kinds of "clicking a link"

Most links behave the way you'd expect: click it, and the page you're
looking at changes to the new URL. But some links (usually the ones
with `target="_blank"` in their HTML, or a "Open in new window" button)
open a completely separate browser tab, leaving the original page
untouched behind it. Your script needs to handle these differently,
because in the second case, the `page` object you already had is now
the *wrong* one, the new content is somewhere else entirely.

## The code, piece by piece

```python
page.locator("article.product_pod h3 a").first.click()
end_url = page.url
```

This is the ordinary case: clicking navigates the same `page` object
to a new URL. Because `.click()` already auto-waits for the resulting
navigation, `page.url` on the very next line correctly reflects the
new page, not a half-loaded old one.

```python
context = browser.new_context()
page = context.new_page()
```

A **browser context** is an isolated session inside a browser, its own
cookies, storage, and set of tabs, similar to opening a private/
incognito window. A context can hold multiple pages (tabs) at once,
which is exactly what we need for the popup case below. Earlier
lessons skipped creating a context explicitly; `browser.new_page()`
was quietly creating a default one for you.

```python
with context.expect_page() as new_page_info:
    page.locator("a", has_text="Click Here").click()
new_tab = new_page_info.value
```

This is the important pattern for popups. `context.expect_page()`
starts listening for a new tab to open *before* the click happens,
inside the `with` block. If we clicked first and only afterward tried
to find the new tab, we'd be racing against the browser, sometimes it
would work, sometimes the new tab wouldn't exist yet, a classic source
of flakiness (see Lesson 9). `new_page_info.value` is the actual new
`Page` object once it exists.

```python
new_tab.wait_for_load_state()
```

The new tab exists as soon as it opens, but its content may still be
loading. Same idea as Lesson 9: wait for a real condition, don't guess.

```python
tab_count = len(context.pages)
```

`context.pages` lists every open tab in this context, useful for
sanity-checking how many tabs are open, or for finding one you didn't
capture directly with `expect_page()`.

## Running it

```bash
uv run python lessons/playwright/02_intermediate/11_multi_page_navigation/lesson.py
```

## Expected output

```
1. Following a link (same tab):
   Started at: https://books.toscrape.com/
   Ended at:   https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html

2. Handling a popup that opens a new tab:
   Tabs open in the context: 2
   Text in the new tab: New Window
```

## Checkpoint

- **Same-tab navigation**: clicking a normal link changes the existing
  `page` object's URL; `.click()` already waits for it.
- **Browser context**: an isolated session (cookies, storage, tabs)
  that a browser can hold several of; a context can have multiple
  pages (tabs) open at once.
- **`context.expect_page()`**: starts listening for a new tab *before*
  the action that opens it, avoiding a race condition where the tab
  isn't captured yet.
- **`context.pages`**: the list of every tab currently open in a
  context.

If anything here still feels unclear, ask before moving to Lesson 12.
