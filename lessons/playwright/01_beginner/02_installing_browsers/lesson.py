"""
Lesson 2: installing the actual browser binaries Playwright drives.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/01_beginner/02_installing_browsers/lesson.py

Lesson 1 explained what Playwright is. Before any code can actually
open a browser (Lesson 3), the browser itself has to exist on this
machine. `uv sync` installs the `playwright` Python package, but that
package is just a driver, it doesn't come with an actual copy of
Chromium. This lesson checks that the binary is there, and installs it
if it isn't.
"""

import subprocess
import sys
from pathlib import Path

# This is where Playwright stores downloaded browsers on Linux and
# macOS. It's not something you're expected to memorize, we're only
# printing it so "install location" isn't a mystery.
CACHE_DIR = Path.home() / ".cache" / "ms-playwright"


def browser_appears_installed() -> bool:
    # We're not being precise here (versions change), just checking
    # whether any chromium-* folder exists under the cache directory.
    # glob() returns a list-like generator of matching paths; wrapping
    # it in any(...) is a common Python idiom for "does at least one
    # match exist" without building the whole list first.
    if not CACHE_DIR.exists():
        return False
    return any(CACHE_DIR.glob("chromium-*"))


def main() -> None:
    print(f"Checking for browser binaries in: {CACHE_DIR}")
    # Python buffers stdout by default, but subprocess.run() below
    # writes straight to the terminal, bypassing that buffer entirely.
    # Without flushing here first, the print() calls above could still
    # be sitting in the buffer when the subprocess's own output lands,
    # making everything print out of order. sys.stdout.flush() forces
    # anything queued up to appear now, before the subprocess runs.
    sys.stdout.flush()

    if browser_appears_installed():
        print("Chromium already appears to be installed.")
    else:
        print("Chromium not found, installing it now (this downloads ~150 MB).")
        sys.stdout.flush()

        # subprocess.run() starts another program and waits for it to
        # finish, exactly like typing this into a terminal yourself.
        # sys.executable is the path to the Python interpreter running
        # this script, using it (instead of a bare "python") makes
        # sure we call the same environment uv set up for this project.
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=False,
        )
        if result.returncode != 0:
            raise SystemExit(
                "playwright install failed. See this project's root "
                "README, Troubleshooting section."
            )

    # --dry-run prints what would be installed (or is already installed)
    # without downloading anything. It's a safe way to double check the
    # install, and to show what Playwright actually manages: a specific
    # pinned version of Chromium, not "whatever Chrome you have".
    print("\nVerifying with a dry run:")
    sys.stdout.flush()
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium", "--dry-run"],
        check=False,
    )


if __name__ == "__main__":
    main()
