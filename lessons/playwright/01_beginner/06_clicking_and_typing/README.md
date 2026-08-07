# Lesson 6: Clicking and typing

## From reading to acting

Every lesson up to this point only read information off a page:
titles, prices, counts. This is the first lesson that changes
something, filling in a form and submitting it, the same two actions
(type, then click) behind the vast majority of anything you'd want an
agent to do on the web: searching, logging in, posting, filtering.

The practice site for this lesson, quotes.toscrape.com, has a `/login`
page built specifically for this: it accepts any username and any
password, there's nothing to sign up for and nothing real to
accidentally break.

## `.fill()` versus `.type()`

Both put text into a field, but differently:

- **`.fill(text)`** clears the field, then sets its value directly, in
  one step. It still fires the events a real browser fires so the
  page's own JavaScript notices the change, it's just not simulating
  individual keystrokes. This is the right default for ordinary text
  inputs, it's fast and reliable.
- **`.type(text, delay=...)`** simulates an actual person typing: one
  keystroke at a time, with an optional delay between each. This is
  slower, and it's specifically for pages whose JavaScript reacts to
  each keystroke as it happens, a live search-as-you-type box, a
  password strength meter, a field that validates character by
  character. For a plain field like this lesson's password box,
  `.fill()` would work equally well; `.type()` is used here so both
  tools are in your hands before you need to choose between them.

## Auto-waiting before a click

`.click()` doesn't just find an element and click it blindly. Before
clicking, Playwright waits for the element to be visible, attached to
the page, stable (not still animating into place), and not covered by
anything else, a loading spinner, a modal, another element on top of
it. If none of that becomes true within a timeout, the click fails
with a clear error instead of clicking the wrong thing, or clicking
nothing at all. This "actionability" checking is one of Playwright's
biggest advantages over older tools, and Lesson 9 covers waiting
strategies in full.

## Waiting after a click that navigates

Submitting this login form causes a real page navigation: the browser
posts the form data and the server sends back a different page. Just
like `page.goto()` in Lesson 4, that navigation needs to finish before
it's safe to read anything from the new page, which is why this lesson
calls `page.wait_for_load_state()` right after the click, with no
arguments it waits for the same "load" event `goto()` waits for by
default.

## The code, piece by piece

```python
page.locator("#username").fill("learner")
```

Clears and sets the username field in one call. `#username` is a CSS
id selector, matching the element with `id="username"`.

```python
page.locator("#password").type("hunter2", delay=20)
```

Types the password one character at a time, with a 20 millisecond
pause between keystrokes, visibly slower if you ran this with
`headless=False`.

```python
page.locator("input[value='Login']").click()
```

An attribute selector: matches an `<input>` whose `value` attribute is
exactly `"Login"`, the submit button on this particular form.

```python
page.wait_for_load_state()
logged_in = page.get_by_text("Logout").count() > 0
```

Waits for the resulting page to load, then checks for a "Logout" link
that only appears once "logged in", a real behavioral confirmation
that the click and fill actually worked, not just that no exception
was raised.

## Running it

```bash
uv run python lessons/playwright/01_beginner/06_clicking_and_typing/lesson.py
```

## Expected output

```
Loaded: Quotes to Scrape
URL after login: https://quotes.toscrape.com/
Login appears successful: True
```

## Checkpoint

- **`.fill(text)`**: sets a field's value directly, in one step, the
  usual default for text inputs.
- **`.type(text, delay=...)`**: simulates real keystrokes one at a
  time, for pages that react to each keystroke.
- **`.click()`**: waits for an element to actually be clickable
  (visible, stable, not covered) before clicking it.
- **Waiting after a navigating action**: a click that submits a form
  triggers a real navigation, wait for it before reading the result,
  the same idea as `page.goto()`.

If anything here still feels unclear, ask before moving to Lesson 7.
