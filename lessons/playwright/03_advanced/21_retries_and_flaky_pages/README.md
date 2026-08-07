# Lesson 21: Retries and flaky pages

## Auto-wait handles "not yet", not "broken right now"

Lesson 09 covered Playwright's auto-waiting: before clicking or reading
an element, Playwright waits for it to actually be there and
interactable, up to a timeout, before giving up. That solves the most
common source of flakiness in browser automation, code that runs faster
than the page does.

But auto-wait has a limit, its default timeout. Real websites sometimes
take longer than that limit through no fault of your script: a slow
server, a temporary network hiccup, a page that's just having a bad
moment. When that happens, the honest answer usually isn't "wait
forever", it's "give up, wait a bit, and try the whole operation again."
That's a retry.

## The pattern: retry with backoff

```python
def retry_with_backoff(operation, attempts=4, initial_delay_seconds=1.0):
    delay = initial_delay_seconds
    for attempt_number in range(1, attempts + 1):
        try:
            return operation(attempt_number)
        except PlaywrightTimeoutError as exc:
            if attempt_number < attempts:
                time.sleep(delay)
                delay *= 2
    raise last_error
```

"Backoff" specifically means the wait *between* retries grows each
time, here it doubles: 1 second, then 2, then 4. This is called
**exponential backoff**, and it matters for a real reason: if a server
is struggling, hitting it again immediately, over and over, at a fixed
interval, tends to make things worse. Waiting longer each time gives it
room to recover.

Notice `operation` is a function, passed in, not called directly, this
function doesn't know anything about Playwright or pages. It only knows
how to retry *any* operation that might raise a timeout. That
separation is deliberate: the retry logic is reusable for anything, not
tied to this one lesson's example.

## The flaky operation

```python
def load_dynamic_content(page: Page, attempt_number: int) -> str:
    page.goto(DYNAMIC_LOADING_URL)
    page.locator("#start button").click()
    timeout_ms = 1500 * (2 ** (attempt_number - 1))
    page.locator("#finish").wait_for(state="visible", timeout=timeout_ms)
    return page.locator("#finish").text_content() or ""
```

`the-internet.herokuapp.com/dynamic_loading/1` hides an element until a
button is clicked, then reveals it a few seconds later, standing in for
a real server that's slow sometimes and fine other times. The first
attempt uses a deliberately tight 1500ms timeout, too short for the
real delay, so the first attempt genuinely fails, not a scripted
pretend failure. Each retry doubles the timeout (`1500 * 2 **
(attempt_number - 1)`), giving the operation more patience each time,
which mirrors a real pattern: an operation that's worth retrying more
patiently, not just repeating identically and hoping.

## Wiring it together

```python
text = retry_with_backoff(lambda attempt: load_dynamic_content(page, attempt), attempts=4)
```

`lambda attempt: load_dynamic_content(page, attempt)` is a small,
unnamed function, Python's shorthand for "wrap this call so it matches
what `retry_with_backoff` expects to call," here, a function that takes
one argument (the attempt number) and does the real work.

## Why not just set one huge timeout?

It's tempting to just pass `timeout=30000` once and call it done. Two
problems with that: first, a single long timeout still fails completely
the moment something genuinely goes wrong (a dropped connection, a
truly dead server), it just takes 30 seconds to find out. Second, a
retry loop can react differently on each attempt, log what's happening,
back off, eventually give up cleanly with a clear message, none of
which a single `wait_for()` call can do on its own.

## Running it

```bash
uv run python lessons/playwright/03_advanced/21_retries_and_flaky_pages/lesson.py
```

## Expected output

```
Loading dynamic content with retry + backoff:
  Attempt 1/4 failed: Locator.wait_for: Timeout 1500ms exceeded.
  Waiting 1.0s before retrying...
  Attempt 2/4 failed: Locator.wait_for: Timeout 3000ms exceeded.
  Waiting 2.0s before retrying...

Succeeded: '\n    Hello World!\n  '
```

Exact attempt counts can vary slightly with network conditions, the
important part is that it eventually succeeds instead of failing the
whole script on the first slow response.

## Checkpoint

- **auto-wait vs retry**: auto-wait handles "the element isn't ready
  yet", retries handle "the whole operation genuinely failed, try it
  again."
- **exponential backoff**: the delay between retries grows each time
  (commonly doubling), giving a struggling server room to recover
  instead of hammering it at a fixed interval.
- **`retry_with_backoff`**: a reusable wrapper that takes any operation
  and retries it a fixed number of times, unrelated to Playwright
  specifically.
- **growing patience per attempt**: besides waiting longer between
  tries, a retry can also give the operation itself more time to
  succeed on each attempt.

If anything here still feels unclear, ask before moving to Lesson 22.
