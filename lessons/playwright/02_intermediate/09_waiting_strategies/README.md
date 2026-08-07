# Lesson 9: Waiting strategies

## Why "just wait a bit" doesn't work

A browser page isn't one instant snapshot, it's a moving target. The
HTML arrives first, then images load, then JavaScript runs and maybe
fetches more data, then it renders that data into the page. If your
script tries to read or click something before that chain finishes, it
either crashes (the element isn't there yet) or reads stale, empty
content.

The tempting fix is to add a fixed pause: "wait 2 seconds, then try."
That's called a **fixed sleep**, and it's the single most common cause
of flaky (sometimes-passes, sometimes-fails) browser scripts. Two
seconds might be plenty on a fast connection and not nearly enough on a
slow one, or when the server is under load. A script built on guesses
about timing is a script that fails unpredictably, often right when you
need it most.

Playwright's answer is to wait for a **condition** instead of a
**duration**: "wait until this element exists," not "wait two
seconds and hope."

## The code, piece by piece

```python
time.sleep(2)
```

This is the anti-pattern, shown once so you can recognize it. It
blocks the whole script for exactly 2 seconds, regardless of whether
the page was ready after 200 milliseconds or would have needed 5
seconds. There is no number here that is ever really correct.

```python
page.wait_for_selector("article.product_pod")
```

This is the fix: wait until an element matching this selector actually
appears in the page, checking repeatedly instead of pausing blindly.
If it never shows up, Playwright raises a clear timeout error (by
default after 30 seconds) instead of your script silently reading
nothing. This is an **explicit wait**: you name exactly what you're
waiting for.

```python
first_title = page.locator("article.product_pod h3 a").first
title = first_title.get_attribute("title")
```

Here's the part worth sitting with: no explicit wait was written at
all, and yet this works reliably. That's because `.locator()` actions
like `.click()`, `.fill()`, and reading attributes all perform
**auto-wait** on your behalf: before doing anything, Playwright checks
that the element is attached to the page, visible, and not covered by
something else, retrying for a few seconds if any of that isn't true
yet. You've actually been relying on this since the beginner tier,
this lesson just makes it visible.

```python
page.wait_for_load_state("networkidle")
```

A different kind of wait: instead of naming an element, this waits
until the network goes quiet (no new requests for a short stretch).
It's useful when you genuinely don't know what element to wait for,
but it's a blunter tool: some pages poll something in the background
forever and never truly go idle, and even when it works, it waits
longer than necessary compared to naming the one element you actually
need. Prefer `wait_for_selector` (or letting auto-wait handle it)
whenever you can name the target.

## Running it

```bash
uv run python lessons/playwright/02_intermediate/09_waiting_strategies/lesson.py
```

## Expected output

```
1. The wrong way: a fixed sleep.
Slept blindly for 2 seconds, hoping the page was ready.

2. The right way: wait_for_selector.
Waited for the actual product listing to appear.

3. Auto-wait: locator actions wait for you automatically.
   First book title: A Light in the Attic

4. wait_for_load_state: waiting on the network instead of an element.
Network went idle, page is fully settled.
```

## Checkpoint

- **Fixed sleep**: pausing for a hardcoded duration, regardless of
  whether the page is actually ready. The main cause of flaky scripts,
  avoid it.
- **Explicit wait (`wait_for_selector`)**: block until a named element
  actually appears, retrying instead of guessing a duration.
- **Auto-wait**: locator actions (`.click()`, `.fill()`, and friends)
  already wait for their target to be visible and stable before acting,
  no extra code needed most of the time.
- **`wait_for_load_state("networkidle")`**: a blunter wait for "the
  network has gone quiet," useful when you can't name a specific
  element, slower and less reliable than naming one when you can.

If anything here still feels unclear, ask before moving to Lesson 10.
