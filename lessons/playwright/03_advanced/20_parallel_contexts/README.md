# Lesson 20: Parallel contexts

## Why isolation matters

Lesson 18 used two contexts on purpose, one to log in and save state,
another to reuse it, exactly because contexts don't share anything
automatically. This lesson leans into that same fact from the other
direction: what happens when several contexts run side by side, each
logged in as someone different, at the same time?

The answer is: nothing leaks between them. A `BrowserContext` is a
self-contained browsing profile, its own cookies, its own local
storage, its own cache. An agent that needs to check a site as three
different users, or scrape the same page from several accounts at
once, needs exactly this: multiple contexts that genuinely don't know
about each other.

## A wrinkle with the sync API and threads

Playwright's sync API (the one this whole course uses) ties a
`sync_playwright()` instance, and everything created from it, a browser,
its contexts, its pages, to the specific thread that started it. It
cannot be handed to a different thread later. This is different from
the async API, which is built for exactly that kind of concurrency.

So true "at the same time" concurrency with the sync API means giving
each thread its own complete, independent Playwright instance, not
sharing one browser object across threads. That's what this lesson
does: `log_in_as()` opens its own `sync_playwright()`, launches its own
browser, and closes everything before returning, all inside whichever
thread calls it.

## The code, piece by piece

```python
def log_in_as(username: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        ...
```

Every single call to this function is fully self-contained. Nothing
here is shared between calls, on purpose, so we can prove isolation
regardless of whether calls happen one after another or genuinely at
the same time.

```python
def run_sequentially(usernames: list[str]) -> list[dict]:
    return [log_in_as(name) for name in usernames]
```

The plain version: one browser, log in, close, repeat. Simple, and
already isolated, just not concurrent.

```python
def run_concurrently(usernames: list[str]) -> list[dict]:
    with ThreadPoolExecutor(max_workers=len(usernames)) as pool:
        results = list(pool.map(log_in_as, usernames))
    return results
```

`ThreadPoolExecutor` runs `log_in_as` for each username on its own
operating system thread. While one thread is waiting on a network
response (which is most of what browser automation spends time doing),
another thread's browser can be making progress. `pool.map()` runs the
function across all inputs and collects the results in the original
order, blocking until every thread has finished.

```python
all_cookies = [r["session_cookie"] for r in sequential_results + concurrent_results]
print(f"All {len(all_cookies)} session cookies unique: {len(set(all_cookies)) == len(all_cookies)}")
```

`quotes.toscrape.com` issues a distinct session cookie for every login,
regardless of which username was typed in. Collecting all six cookies
into a `set` (which automatically drops duplicates) and comparing its
length back to the original list length is a quick way to check "were
any two of these actually the same": if isolation had failed somewhere,
we'd see fewer unique cookies than logins.

## Running it

```bash
uv run python lessons/playwright/03_advanced/20_parallel_contexts/lesson.py
```

## Expected output

```
=== Sequential contexts ===
  alice: session cookie = eyJjc3JmX3Rva2VuIjoi...
  bob: session cookie = eyJjc3JmX3Rva2VuIjoi...
  carol: session cookie = eyJjc3JmX3Rva2VuIjoi...

=== Concurrent contexts (threads) ===
  alice: session cookie = eyJjc3JmX3Rva2VuIjoi...
  bob: session cookie = eyJjc3JmX3Rva2VuIjoi...
  carol: session cookie = eyJjc3JmX3Rva2VuIjoi...

All 6 session cookies unique: True
```

The actual cookie values are long, encoded strings and will differ on
every run, what matters is that all six are unique.

## Checkpoint

- **`BrowserContext`**: an isolated browsing profile, its own cookies
  and storage, independent of every other context.
- **why isolation matters**: agents that act as multiple users, or run
  many scraping jobs at once, need contexts that genuinely can't leak
  into each other.
- **sync API and threads**: a `sync_playwright()` instance is tied to
  the thread that created it, so real concurrency means one full,
  independent Playwright instance per thread, not one browser shared
  across threads.
- **`ThreadPoolExecutor`**: runs a function across multiple inputs on
  separate threads, useful here because most of the wait time in
  browser automation is network I/O, not CPU work.

If anything here still feels unclear, ask before moving to Lesson 21.
