# Lesson 22: Running headless in Docker

## Headless has been the default all along

Every single lesson in this course, from Lesson 3 onward, called
`p.chromium.launch()` with no arguments, and it worked, no window ever
popped up on screen. That's because `headless=True` is Playwright's
default. "Headless" means the browser runs with no visible window at
all, it still parses HTML, runs JavaScript, and renders pages, just
entirely in memory, with nothing drawn to a screen.

This lesson makes that default explicit, then walks through what
actually changes when the exact same kind of script runs inside a
Docker container or a CI runner, instead of on a laptop with a full
desktop environment.

## Why headless matters for where code actually runs

A real desktop has a **display server** (on Linux, X11 or Wayland),
software responsible for actually drawing windows to a screen. A
typical CI runner or a minimal Docker container has none of that, no
monitor, no windowing system, nothing to draw a browser window onto
even if you wanted one.

`headless=True` sidesteps the problem entirely: it never asks for a
window in the first place. That's exactly why browser automation is
possible at all inside CI pipelines and containers, environments built
to run code, not to display anything.

```python
browser = p.chromium.launch(headless=True)
```

The opposite, `headless=False`, opens a real, visible browser window,
genuinely useful while writing and debugging a script on your own
machine, so you can watch it click around. But it requires a display
server to exist, run it in a typical container or CI runner and it
fails outright, there's nothing for it to open a window onto.

## Two flags that matter specifically inside containers

```python
browser = p.chromium.launch(
    headless=True,
    args=["--disable-dev-shm-usage", "--no-sandbox"],
)
```

**`--disable-dev-shm-usage`**: Chrome normally uses `/dev/shm`, a chunk
of shared memory, as fast scratch space. Docker gives containers a
small `/dev/shm` by default (64MB), often too little for Chrome on
content-heavy pages, which causes crashes. This flag tells Chrome to
fall back to disk-backed temp files instead, slower, but reliable
inside a default container.

**`--no-sandbox`**: disables one of Chrome's OS-level security
sandboxes. Some container configurations, and running as root inside a
container (common with default base images), can conflict with that
sandbox. This flag is standard advice for CI and Docker, but it's a
real tradeoff, less isolation, so it belongs in trusted, disposable
CI/container environments, not as a blanket default everywhere.

## Detecting the environment

```python
running_in_docker = os.path.exists("/.dockerenv")
running_in_ci = os.environ.get("CI", "").lower() == "true"
```

`/.dockerenv` is a file Docker itself creates inside every container it
starts, its presence is a reliable, if slightly informal, signal that a
process is running inside a container. The `CI` environment variable is
a de facto standard, GitHub Actions, GitLab CI, CircleCI, and most
other providers all set it to `"true"` on every build runner. Neither
check is required for Playwright itself to work, they're just useful
for a script that wants to log, or behave slightly differently, when it
detects it's running somewhere automated instead of on a developer's
own machine.

## A minimal Dockerfile

Actually building and running this isn't executable in this lesson
environment, but here is a real, minimal Dockerfile that runs a
Playwright script like the ones in this course:

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY . .

# The official Playwright image already has Chromium and its OS-level
# dependencies preinstalled, so no separate "playwright install" step
# is needed here, unlike a plain python:3.x base image.
CMD ["uv", "run", "python", "lessons/playwright/03_advanced/22_running_headless_in_docker/lesson.py"]
```

The key idea: Microsoft publishes an official Playwright base image
with Chromium, Firefox, WebKit, and all their OS-level dependencies
(fonts, shared libraries, and so on) already installed. Starting from a
plain `python:3.x` image instead is possible, but then `uv run
playwright install --with-deps chromium` has to run as a build step,
pulling down both the browser binary and a long list of system
packages by hand.

## Running it

```bash
uv run python lessons/playwright/03_advanced/22_running_headless_in_docker/lesson.py
```

## Expected output

Locally, outside a container:

```
Environment diagnostics:
  Python version: 3.14.4
  Platform: linux (x86_64)
  Running inside Docker: False
  Running inside CI: False

Loaded page headlessly, title: 'All products | Books to Scrape - Sandbox'

Loaded with container-friendly args, title: 'All products | Books to Scrape - Sandbox'
```

Inside a real Docker container, `Running inside Docker` would print
`True`, everything else stays the same, since headless Chromium behaves
identically either way once the right launch flags are in place.

## Checkpoint

- **headless**: a browser mode with no visible window, rendering
  entirely in memory, the default this whole course has used since
  Lesson 3.
- **why containers need it**: CI runners and minimal containers have no
  display server, `headless=False` fails outright in that environment.
- **`--disable-dev-shm-usage`**: works around Docker's small default
  shared-memory allocation, which otherwise crashes Chrome on
  content-heavy pages.
- **`--no-sandbox`**: disables an OS-level Chrome sandbox that can
  conflict with some container setups, a real isolation tradeoff, best
  limited to trusted CI/container environments.
- **official Playwright Docker image**: comes with browsers and their
  system dependencies preinstalled, avoiding a manual
  `playwright install --with-deps` build step.

If anything here still feels unclear, ask before moving to Lesson 23.
