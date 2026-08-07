# Lesson 18: Authentication and storage state

## The problem: logging in is slow and repetitive

Every lesson so far started a browser context from nothing: no cookies,
no session, no memory of anything that happened before. That's fine for
scraping a public page, but it breaks down the moment a site requires
logging in. If an agent needs to check the same authenticated site ten
times a day, filling out a login form ten separate times is slow,
fragile (login forms sometimes have CAPTCHAs, rate limits, or two-factor
prompts that a script can't handle), and wasteful.

The fix is to log in once, save whatever proves we're logged in, and
reuse that proof on every future run. That "proof" is almost always just
cookies, plus sometimes a bit of local storage, and Playwright has a
built-in way to capture and restore exactly that: `storage_state`.

## What storage_state actually is

When you log into a website normally, in a real browser, the server
sends back a cookie that says, roughly, "this browser is user X,
trust it." Your browser stores that cookie and attaches it to every
future request to that site, which is how the site keeps recognizing
you without asking for your password again.

`context.storage_state()` captures that same information, cookies and
local storage, as a plain JSON file. `new_context(storage_state=...)`
does the reverse: it pre-loads a fresh context with that JSON before a
single page has even loaded. The browser doesn't "remember" logging in,
it just starts out holding cookies that say it already did.

## The code, piece by piece

```python
STATE_FILE = Path(__file__).parent / "auth_state.json"
```

`Path(__file__).parent` means "the folder this script lives in," so the
saved session file shows up right next to `lesson.py`, not buried in a
system temp directory somewhere you'd never think to look.

### Step 1: log in with a blank context

```python
context = browser.new_context()
page = context.new_page()
page.goto(LOGIN_URL)
page.locator("#username").fill("student")
page.locator("#password").fill("learning-playwright")
page.locator("input[type='submit']").click()
```

`quotes.toscrape.com/login` is a practice site that accepts any
username and password at all, it exists specifically for exercises like
this one. A real login would need real credentials, which should come
from environment variables or a secrets manager, never typed directly
into a script.

```python
page.wait_for_selector("a[href='/logout']")
```

The page shows a "Logout" link only when a session is active. Waiting
for it to appear is our proof the login actually succeeded, before we
trust anything enough to save it.

### Step 2: save the session

```python
context.storage_state(path=str(STATE_FILE))
```

This writes every cookie the context is currently holding to
`auth_state.json`. Open that file in a text editor after running this
lesson (before it gets cleaned up at the end) and you'll see plain JSON:
a list of cookies, each with a name, value, domain, and expiry.

### Step 3: reuse the session in a brand new context

```python
context = browser.new_context(storage_state=str(STATE_FILE))
page = context.new_page()
page.goto("https://quotes.toscrape.com/")
```

This context has never called `.fill()` or `.click()` on a login form,
it's entirely new. But because it was created with `storage_state=`, it
already holds the saved cookies, so the site treats it as already
logged in the instant the homepage loads.

```python
logout_link = page.locator("a[href='/logout']")
already_logged_in = logout_link.count() > 0
```

`.count()` returns how many elements matched, `0` if none did. This is
a quick way to check "does this exist on the page" without raising an
error the way `.click()` would if the element were missing.

## When this matters for agents

An agent that browses the web on your behalf will often need to act as
a logged-in user: checking an inbox, reading a private dashboard,
submitting a form that requires an account. Re-running the login flow
on every single tool call is slow and adds a fragile step an LLM has no
business improvising its way through. Logging in once (usually by a
human, out of band) and handing the agent a saved `storage_state` file
is the standard pattern: the agent gets to act as an authenticated user
without ever seeing a password.

## Running it

```bash
uv run python lessons/playwright/03_advanced/18_authentication_and_storage_state/lesson.py
```

## Expected output

```
Logged in successfully, 'Logout' link is visible.
Saved session state to auth_state.json
Already authenticated on a fresh context: True
Removed auth_state.json
```

## Checkpoint

- **`storage_state`**: a JSON snapshot of a context's cookies and local
  storage, everything that proves a session is authenticated.
- **`context.storage_state(path=...)`**: saves the current context's
  state to a file.
- **`browser.new_context(storage_state=...)`**: pre-loads a brand new
  context with a previously saved state, skipping the login form
  entirely.
- **why it matters**: real credentials shouldn't live in scripts, and
  agents shouldn't repeat a slow, fragile login flow on every run.

If anything here still feels unclear, ask before moving to Lesson 19.
