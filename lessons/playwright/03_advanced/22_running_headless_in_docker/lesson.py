"""
Lesson 22: headless mode, container and CI considerations.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/03_advanced/22_running_headless_in_docker/lesson.py

Every launch in this course so far used p.chromium.launch() with no
arguments, and it worked, that's because headless=True is already the
default. This lesson makes that default explicit, and walks through
what changes (and what to double check) when the same script runs
inside a container instead of on your own machine.
"""

import os
import platform
import sys

from playwright.sync_api import sync_playwright


def print_environment_diagnostics() -> None:
    """Print a few facts useful for answering "will this run in CI or
    Docker the same way it runs on my machine?" before we even launch a
    browser."""
    print("Environment diagnostics:")
    print(f"  Python version: {sys.version.split()[0]}")
    print(f"  Platform: {sys.platform} ({platform.machine()})")

    # /.dockerenv is a file Docker itself creates inside every container
    # it starts, nothing else creates it, so its presence is a reliable
    # signal "this process is running inside a Docker container."
    running_in_docker = os.path.exists("/.dockerenv")
    print(f"  Running inside Docker: {running_in_docker}")

    # Most CI providers (GitHub Actions, GitLab CI, CircleCI, and others)
    # set a "CI" environment variable to "true" on every build runner, a
    # de facto standard, useful for scripts that should behave slightly
    # differently in automated environments (e.g. always headless, no
    # interactive prompts).
    running_in_ci = os.environ.get("CI", "").lower() == "true"
    print(f"  Running inside CI: {running_in_ci}")


def launch_headless_and_headful_explained() -> None:
    with sync_playwright() as p:
        # headless=True is already the default, every previous lesson in
        # this course used it implicitly. Writing it out here makes the
        # choice visible: no visible window opens anywhere, the browser
        # renders pages entirely in memory. This is what makes browser
        # automation possible on a server or in a container with no
        # display attached at all.
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://books.toscrape.com/")
        title = page.title()
        print(f"\nLoaded page headlessly, title: {title!r}")
        browser.close()

        # headless=False would try to open a real, visible browser
        # window. That requires a display server (on Linux, an X11 or
        # Wayland session), which containers and most CI runners simply
        # don't have. Uncommenting the line below on a typical CI runner
        # or minimal Docker image would raise an error, not open a
        # window, there's nothing for it to open onto.
        #
        # browser = p.chromium.launch(headless=False)


def launch_with_container_friendly_args() -> None:
    """Extra launch arguments that matter specifically inside containers,
    less commonly needed on a normal desktop."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                # Chrome normally uses /dev/shm (shared memory) as scratch
                # space. Docker gives containers a very small /dev/shm by
                # default (64MB), which is often too little for Chrome
                # and causes crashes on pages with a lot of content.
                # --disable-dev-shm-usage tells Chrome to use disk-backed
                # temp files instead, slower, but far more reliable
                # inside a default container.
                "--disable-dev-shm-usage",
                # --no-sandbox disables Chrome's OS-level sandboxing.
                # Chrome's sandbox relies on kernel features that some
                # container setups restrict, and running as root inside
                # a container (as many base images do by default) can
                # trip it up too. This flag is common advice for CI and
                # Docker, but it does reduce isolation, so it's best
                # limited to trusted, disposable CI/container
                # environments, not a general-purpose default.
                "--no-sandbox",
            ],
        )
        page = browser.new_page()
        page.goto("https://books.toscrape.com/")
        print(f"Loaded with container-friendly args, title: {page.title()!r}")
        browser.close()


def main() -> None:
    print_environment_diagnostics()
    launch_headless_and_headful_explained()
    print()
    launch_with_container_friendly_args()


if __name__ == "__main__":
    main()
