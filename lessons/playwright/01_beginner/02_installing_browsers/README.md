# Lesson 2: Installing the browsers

## Two separate installs

Playwright is unusual compared to most Python packages, because
installing it doesn't fully set it up. `uv sync` installs the
`playwright` Python package, the code that knows how to talk to a
browser, but it does not install any actual browser. That's a second,
separate step, run through Playwright's own command line tool:

```bash
uv run playwright install chromium
```

Think of it like the difference between installing `psycopg` (the
Postgres client library, from the pgvector course) and installing
Postgres itself. One is a library your code imports, the other is the
real program doing the work. Here, `playwright` (the Python package)
is the library, and Chromium (the browser) is the real program.

## Why a separate download

Playwright doesn't use whatever browser happens to already be on your
machine, your regular Chrome or Firefox. Instead, it downloads its own
pinned copies of Chromium, Firefox, and WebKit, matched exactly to the
version of the `playwright` package you have installed. This matters
because browser internals change constantly, and Playwright's
automation code is written against a specific, known version. Using
your everyday browser instead would mean things silently break every
time that browser auto-updates.

This course only uses Chromium, the open-source engine behind Google
Chrome, which is why every install command in this course says
`playwright install chromium` and not the bare `playwright install`
(which would download all three engines).

## Where it goes

On Linux and macOS, downloaded browsers live in
`~/.cache/ms-playwright/`, in a folder named after the specific
browser and build, e.g. `chromium-1234`. You never need to touch this
folder directly, Playwright manages it, but it's worth knowing it
exists so "where did that 150 MB go" has an answer.

## The code, piece by piece

```python
CACHE_DIR = Path.home() / ".cache" / "ms-playwright"
```

`Path.home()` gives your home directory as a `Path` object, and `/` is
overloaded here to join path segments, this is `pathlib`'s way of
building a path without manually gluing strings together with slashes.

```python
def browser_appears_installed() -> bool:
    if not CACHE_DIR.exists():
        return False
    return any(CACHE_DIR.glob("chromium-*"))
```

`.glob("chromium-*")` finds every folder in the cache directory whose
name starts with `chromium-`. `any(...)` returns `True` the moment it
finds one match, without needing to check all of them, a common
Python idiom for "does at least one exist."

```python
sys.stdout.flush()
```

Python buffers what `print()` writes, holding it briefly before it
actually appears, while `subprocess.run()` writes straight to the
terminal, bypassing that buffer entirely. Without flushing first, a
`print()` call just before a `subprocess.run()` call can end up
appearing after the subprocess's own output, out of the order it was
actually written in. `sys.stdout.flush()` forces anything queued up
to appear immediately, keeping the output in the order you'd expect.

```python
result = subprocess.run(
    [sys.executable, "-m", "playwright", "install", "chromium"],
    check=False,
)
```

`subprocess.run()` runs another program from inside Python and waits
for it to finish, exactly as if you'd typed the equivalent command
yourself. `sys.executable` is the path to the exact Python interpreter
running this script, using it here (rather than assuming a `python`
command exists on the PATH) makes sure the install runs inside the
same `uv`-managed environment as everything else in this project.
`check=False` means "don't raise an exception automatically if this
fails", we check `result.returncode` ourselves instead, so we can give
a clearer error message pointing at this project's root
[Troubleshooting section](../../../../README.md#troubleshooting).

```python
subprocess.run(
    [sys.executable, "-m", "playwright", "install", "chromium", "--dry-run"],
    check=False,
)
```

`--dry-run` asks Playwright to report what it would install (or
confirm what's already installed) without downloading anything. It's a
safe way to verify the install worked, and it prints useful details
like the exact Chrome for Testing version and the install path.

## Running it

```bash
uv run python lessons/playwright/01_beginner/02_installing_browsers/lesson.py
```

## Expected output

If Chromium is already installed (as it will be for the rest of this
course, since this lesson installs it the first time):

```
Checking for browser binaries in: /home/you/.cache/ms-playwright
Chromium already appears to be installed.

Verifying with a dry run:
Chrome for Testing 151.0.7922.34 (playwright chromium v1234)
  Install location:    /home/you/.cache/ms-playwright/chromium-1234
  Download url:        https://cdn.playwright.dev/builds/cft/151.0.7922.34/linux64/chrome-linux64.zip
...
```

The first time you ever run this, you'll instead see a download
progress message before the "already installed" line appears.

## Checkpoint

- **Two installs, not one**: `uv sync` installs the `playwright`
  Python package, `playwright install chromium` installs the actual
  browser binary. Both are required.
- **Pinned browsers**: Playwright downloads its own copy of Chromium
  matched to its own version, it doesn't reuse your everyday browser.
- **Install location**: `~/.cache/ms-playwright/` on Linux and macOS.
- **`--dry-run`**: reports what would be installed, or confirms what
  already is, without downloading anything.
- **`sys.stdout.flush()`**: forces buffered `print()` output to appear
  immediately, so it doesn't get reordered relative to a subprocess's
  own direct writes to the terminal.

If anything here still feels unclear, ask before moving to Lesson 3.
