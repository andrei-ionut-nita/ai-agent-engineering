# Lesson 15: Wrapping Playwright as a tool

## Building the function before the AI ever sees it

This course's prerequisite (see the [course README](../../README.md))
is Lessons 13 and 14 of the langchain course. There, a calculator was
built as a plain Python function first, tested directly with no model
involved, and only afterward wrapped with `@tool` and handed to a
model. This lesson follows that exact same shape, on purpose: get
`browse(url)` right and predictable on its own first, so Lesson 16 can
focus entirely on how a model decides to use it, not on whether the
function itself works.

## The code, piece by piece

```python
def browse(url: str) -> str:
```

The whole interface a future AI will ever see: one string in (a URL),
one string out (the page's text). No Playwright-specific types cross
this boundary, on purpose, a model doesn't know what a `Page` object
is, and it doesn't need to.

```python
try:
    page.goto(url, timeout=15_000)
except Exception as exc:
    browser.close()
    return f"Could not load {url}: {exc}"
```

Normal Python code often lets exceptions propagate, so whoever called
it can decide how to handle a failure. A tool function can't rely on
that: once a model is calling this (Lesson 16), there's no `try`/
`except` on the model's side, it can only read whatever text comes
back. So failures have to become a **normal return value**, a string
describing what went wrong, not something that crashes the whole
program.

```python
text = page.locator("body").inner_text()
```

`inner_text()` (unlike `inner_html()`, used nowhere in this course
until now) strips away every tag, script, and stylesheet, returning
only the text a human eye would actually read on the rendered page.
That's the right shape for a model: raw HTML is mostly markup a model
doesn't need, and would burn through its limited context window for no
benefit.

```python
max_chars = 4000
if len(text) > max_chars:
    text = text[:max_chars] + "\n...(truncated)"
```

Real pages can be huge. A model's context window is a hard limit, not
a suggestion, so trimming here keeps the tool's output small and
predictable no matter what page it's pointed at. `text[:max_chars]`
is Python slicing again (seen in Lesson 13): "the first `max_chars`
characters."

## Why no `@tool` decorator yet

`@tool` (from `langchain_core.tools`, used starting next lesson) adds
metadata for a model: a name, a description, an argument schema. None
of that is useful until a model actually exists to read it. Keeping
this lesson AI-free means you can test and trust `browse()` entirely
on its own terms, the same discipline good software engineering
already asks for: build and verify a unit in isolation before
composing it into something bigger.

## Running it

```bash
uv run python lessons/playwright/02_intermediate/15_wrapping_playwright_as_a_tool/lesson.py
```

## Expected output

```
Quotes to Scrape
Login
"The world as we have created it is a process of our thinking. It cannot be
changed without changing our thinking."
by Albert Einstein (about)
Tags: change deep-thoughts thinking world
...
---

Could not load https://this-domain-does-not-exist-12345.invalid/: Page.goto:
net::ERR_NAME_NOT_RESOLVED at https://this-domain-does-not-exist-12345.invalid/
```

The exact error text varies by OS and network setup, but it will
always come back as a plain string, never a crash.

## Checkpoint

- **`browse(url) -> str`**: a plain, LLM-agnostic function, string in,
  string out, no knowledge that a model will ever call it.
- **Failures become return values, not exceptions**: a tool function a
  model will call can't rely on a `try`/`except` on the caller's side,
  it has to report failure as ordinary text.
- **`inner_text()` vs `inner_html()`**: `inner_text()` gives you what a
  human sees rendered, with tags and scripts stripped, the right shape
  to hand to a model.
- **Truncating output**: a model's context window is a hard limit;
  trimming long results keeps a tool's output predictable.

If anything here still feels unclear, ask before moving to Lesson 16,
where this exact function gets wrapped with `@tool` and handed to a
model.
