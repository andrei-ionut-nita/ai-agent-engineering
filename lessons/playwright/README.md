# Course index

A linear, one-concept-per-lesson path through **Playwright**, the
browser automation library that gives an agent "hands" on the web:
navigating pages, clicking things, filling in forms, and reading back
whatever's on screen. Do these in order, top to bottom, each lesson
folder has a `README.md` (read first) and a `lesson.py` (run second).
Don't move to the next lesson until the current one's checkpoint
questions feel solid.

This course assumes you've done the [langchain](../langchain/) course
through the tools lessons (Lessons 13-16), where `@tool` and
`bind_tools` were introduced. Playwright lessons build ordinary
Python functions first, browser-only, no LLM involved, then wire the
same functions in as agent tools later in the course, exactly like any
other `@tool`.

Setup: `uv sync` already installs the `playwright` Python package, but
the browser binaries themselves are a separate download handled by
Playwright's own CLI, run once from the project root:

```bash
uv run playwright install chromium
```

A `GOOGLE_API_KEY` in `.env` is only needed starting at Lesson 16,
where an LLM is first wired to a Playwright tool. Then, from the
project root:

```bash
uv run python lessons/playwright/<tier>/<NN>_<name>/lesson.py
```

## Beginner: controlling a browser

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_playwright](01_beginner/01_what_is_playwright/) | Browser automation, why agents need a browser at all |
| 02 | [installing_browsers](01_beginner/02_installing_browsers/) | `playwright install`, the browser binaries |
| 03 | [launching_a_browser](01_beginner/03_launching_a_browser/) | `sync_playwright()`, `chromium.launch()` |
| 04 | [navigating_to_a_page](01_beginner/04_navigating_to_a_page/) | `page.goto()`, waiting for a page to load |
| 05 | [locators_and_selecting_elements](01_beginner/05_locators_and_selecting_elements/) | `page.locator()`, CSS/text/role selectors |
| 06 | [clicking_and_typing](01_beginner/06_clicking_and_typing/) | `.click()`, `.fill()`, `.type()` |
| 07 | [reading_content](01_beginner/07_reading_content/) | `.text_content()`, `.inner_html()`, pulling data off a page |
| 08 | [beginner_checkpoint_project](01_beginner/08_beginner_checkpoint_project/) | **Checkpoint:** scrape a page's headlines into a list |

## Intermediate: real pages, real forms, and a first tool wiring

| # | Lesson | Concept |
|---|--------|---------|
| 09 | [waiting_strategies](02_intermediate/09_waiting_strategies/) | Auto-wait, `wait_for_selector`, avoiding flaky scripts |
| 10 | [filling_and_submitting_forms](02_intermediate/10_filling_and_submitting_forms/) | Text fields, checkboxes, dropdowns, submit |
| 11 | [multi_page_navigation](02_intermediate/11_multi_page_navigation/) | Following links, handling new tabs and popups |
| 12 | [screenshots_and_pdfs](02_intermediate/12_screenshots_and_pdfs/) | `page.screenshot()`, full-page capture, saving a PDF |
| 13 | [extracting_structured_data](02_intermediate/13_extracting_structured_data/) | Scraping a page into typed Pydantic models |
| 14 | [handling_dialogs_and_downloads](02_intermediate/14_handling_dialogs_and_downloads/) | `page.on("dialog")`, triggering and saving file downloads |
| 15 | [wrapping_playwright_as_a_tool](02_intermediate/15_wrapping_playwright_as_a_tool/) | A plain `browse(url)` function, ready to become a tool |
| 16 | [wiring_it_into_langchain](02_intermediate/16_wiring_it_into_langchain/) | The browse tool bound to a Gemini agent with `@tool` |
| 17 | [intermediate_checkpoint_project](02_intermediate/17_intermediate_checkpoint_project/) | **Checkpoint:** an agent that searches a site and reports back |

## Advanced: production-shaped browser automation

| # | Lesson | Concept |
|---|--------|---------|
| 18 | [authentication_and_storage_state](03_advanced/18_authentication_and_storage_state/) | Logging in once, reusing `storage_state` across runs |
| 19 | [network_interception](03_advanced/19_network_interception/) | `page.route()`, mocking and blocking requests |
| 20 | [parallel_contexts](03_advanced/20_parallel_contexts/) | Multiple isolated browser contexts running at once |
| 21 | [retries_and_flaky_pages](03_advanced/21_retries_and_flaky_pages/) | Resilience patterns for real, unpredictable sites |
| 22 | [running_headless_in_docker](03_advanced/22_running_headless_in_docker/) | Headless mode, container/CI considerations |
| 23 | [safety_with_untrusted_pages](03_advanced/23_safety_with_untrusted_pages/) | Sandboxing a browsing agent, prompt injection via page content |
| 24 | [advanced_capstone_project](03_advanced/24_advanced_capstone_project/) | **Capstone:** an end-to-end web research agent |
