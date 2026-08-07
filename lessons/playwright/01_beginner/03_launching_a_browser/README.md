# Lesson 3: Launching a browser

## Three nested things: Playwright, browser, page

Getting from "nothing" to "a page I can read" involves three layers,
and it helps to keep them straight before writing any code:

1. **Playwright itself**, the driver process that knows how to talk
   to browsers. You get a handle to it from `sync_playwright()`.
2. **A browser**, one running instance of Chromium, launched from
   that driver with `p.chromium.launch()`. This is an actual OS
   process, you could see it in your system's process list.
3. **A context, then a page**, inside that browser. A context is an
   isolated session (its own cookies, its own storage, like a fresh
   private browsing window), and a page is one tab inside it. You'll
   almost always want at least one context and one page before you
   can do anything useful.

This lesson only gets as far as creating an empty context and page,
proving the browser is alive. Lesson 4 actually navigates somewhere.

## Why `with sync_playwright() as p:`

`sync_playwright()` returns something Python calls a context manager,
which is why it's used with `with ... as p:` instead of a plain
assignment. The practical benefit: whatever happens inside that
indented block, even an error, Python guarantees the driver process
gets shut down when the block ends. Every lesson from here on uses
this same `with` pattern, and every browser, context, and page opened
inside it gets explicitly closed before the block ends.

## Headless versus headed

`p.chromium.launch(headless=True)` starts a browser with no visible
window, this is the default, and it's what you want for scripts,
servers, and automated agents: no display needed, faster, lighter.
Passing `headless=False` instead opens a real window you can watch,
which is genuinely useful while you're first learning, seeing the
browser click and type in real time makes debugging far easier. This
course defaults to headless in its code, but try flipping it to
`False` locally at least once, just to watch it work.

## The code, piece by piece

```python
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
```

Starts the driver, then starts one Chromium process. `browser` is now
a live, running browser, just with nothing open in it yet.

```python
    print("Is connected:", browser.is_connected())
```

`.is_connected()` checks whether Playwright still has a working
connection to that browser process. Useful as a sanity check, and a
preview of the kind of state you can always ask a browser object
about.

```python
    context = browser.new_context()
    page = context.new_page()
```

A fresh, isolated session, then one tab inside it. Nothing is loaded
into that tab yet, it exists but shows a blank page, `about:blank`.

```python
    page.close()
    context.close()
    browser.close()
```

Closed in the reverse order they were opened: page first, then the
context that held it, then the browser process itself. Skipping this
doesn't crash anything immediately, but it leaves a real Chromium
process running in the background, doing nothing, until your program
exits or you kill it manually.

## Running it

```bash
uv run python lessons/playwright/01_beginner/03_launching_a_browser/lesson.py
```

## Expected output

```
Browser launched.
Browser type: chromium
Is connected: True
Created one browser context and one page inside it.
Everything closed cleanly.
```

## Checkpoint

- **Playwright, browser, context, page**: four layers, driver process,
  running browser, isolated session, single tab, each nested inside
  the last.
- **`sync_playwright()`**: a context manager, use it with `with ... as
  p:` so the driver shuts down cleanly even if something errors.
- **`headless=True` vs `headless=False`**: no visible window (default,
  for scripts and servers) vs a real window you can watch (useful
  while developing).
- **Always close what you open**: page, then context, then browser,
  in that order, or you'll leave orphaned browser processes running.

If anything here still feels unclear, ask before moving to Lesson 4.
