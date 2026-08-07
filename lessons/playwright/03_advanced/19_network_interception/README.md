# Lesson 19: Network interception

## Getting in between the browser and the network

Every previous lesson let requests go wherever they naturally go: the
browser asks for a page, the server answers, Playwright reads whatever
came back. `page.route()` breaks that chain on purpose. It lets your
script step in front of matching requests, before they ever leave the
browser, and decide what happens: answer with fake data, block the
request entirely, or let it through untouched.

This matters for a few real reasons: testing how a page behaves on a
slow or broken network without actually waiting for one, avoiding
loading heavy assets (images, fonts, video) you don't care about, and
building deterministic tests against a mocked API instead of a real one
that might change.

## Two kinds of interception

**Mocking**, answering a request yourself instead of letting it reach
the real server:

```python
def mock_json_response(route: Route) -> None:
    route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(fake_body),
    )
```

`route.fulfill()` completes the request with whatever you give it. As
far as the page is concerned, this response really did come from the
server, it has no way to tell the difference.

**Blocking**, refusing a request outright:

```python
def block_images(route: Route) -> None:
    route.abort()
```

`route.abort()` makes the request fail, the same as a real network
error. The page keeps running, it just never gets that particular
resource.

## The code, piece by piece

### Setting up a route

```python
page.route("https://httpbin.org/json", mock_json_response)
page.goto("https://httpbin.org/json")
```

`page.route(pattern, handler)` has to be called *before* the matching
request is made, it's registering a rule, not reacting to something
that already happened. The pattern can be an exact URL, like here, or a
glob pattern for matching many URLs at once.

### Matching many URLs with a glob pattern

```python
page.route("**/*.{png,jpg,jpeg}", block_images)
```

`**` matches any sequence of characters, including slashes, so this
matches any request URL that ends in `.png`, `.jpg`, or `.jpeg`,
anywhere on the page, not just the top-level document.

### Proving it actually happened

```python
blocked_urls: list[str] = []
page.on("requestfailed", lambda request: blocked_urls.append(request.url))
```

`page.on("requestfailed", ...)` is an event listener: instead of
returning a value, it runs the given function every time that event
fires, for as long as the page exists. An aborted request fires exactly
this event, which is how the lesson proves images really were blocked,
not just assumed to be.

### Confirming the page still works

```python
first_title = page.locator("article.product_pod h3 a").first
print("First book title still readable:", first_title.get_attribute("title"))
```

Blocking images didn't break the page: book titles are plain HTML text,
not pictures, so the content that actually matters for scraping came
through completely unaffected. This is the practical payoff of
blocking: cutting bandwidth and load time on the parts of a page you
don't care about, without touching the parts you do.

## Running it

```bash
uv run python lessons/playwright/03_advanced/19_network_interception/lesson.py
```

## Expected output

```
=== Mocking a response ===
Response body (should be our fake data):
{"slideshow": {"author": "Not the real httpbin", "title": "Mocked entirely by Playwright"}}

=== Blocking requests ===

Blocked 21 image request(s).
First blocked URL: https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg
First book title still readable: A Light in the Attic
```

The exact blocked count and image URL may vary slightly if the site
changes its catalog images, the important part is that it's a positive
number and the book title still reads correctly.

## Checkpoint

- **`page.route(pattern, handler)`**: registers a rule that intercepts
  matching requests before they leave the browser. Must be set up
  before the matching request happens.
- **`route.fulfill(...)`**: answers a request with a response you make
  up yourself, the real server is never contacted.
- **`route.abort()`**: fails a request outright, like a network error.
- **glob patterns**: `**` matches any characters including slashes,
  useful for matching a whole category of URLs (all images, all API
  calls to one host) at once.

If anything here still feels unclear, ask before moving to Lesson 20.
