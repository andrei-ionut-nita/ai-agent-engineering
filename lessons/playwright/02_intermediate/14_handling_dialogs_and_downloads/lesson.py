"""
Lesson 14: handling dialogs and downloads.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/02_intermediate/14_handling_dialogs_and_downloads/lesson.py

Two more things pages do that break a naive script: native browser
dialogs (alert/confirm/prompt boxes, which pause the whole page until
answered), and file downloads (which don't load like a normal page at
all). This lesson handles both.
"""

from pathlib import Path

from playwright.sync_api import Dialog, sync_playwright

OUTPUT_DIR = Path(__file__).parent / "output"


def dialog_demo() -> str:
    """Accepts a native JavaScript alert() instead of letting it hang."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://the-internet.herokuapp.com/javascript_alerts")

        # Native browser dialogs (alert, confirm, prompt) are NOT part of
        # the page's HTML, they're the browser itself pausing everything
        # until a human clicks OK or Cancel. Left unhandled, a headless
        # script would just hang forever waiting for a click that will
        # never come. page.on("dialog", ...) registers a handler that
        # fires the moment one appears, so we can respond automatically.
        captured_message = ""

        def handle_dialog(dialog: Dialog) -> None:
            nonlocal captured_message
            captured_message = dialog.message
            # .accept() clicks "OK". A confirm() dialog could instead be
            # dismissed with dialog.dismiss(), which clicks "Cancel".
            dialog.accept()

        page.on("dialog", handle_dialog)

        # This button runs JavaScript's alert("I am a JS Alert") when
        # clicked. Because we registered the handler above BEFORE
        # clicking, Playwright intercepts the dialog automatically,
        # there's nothing further we need to do here.
        page.locator("text=Click for JS Alert").click()

        # The page shows the dialog's result in this element after it's
        # been handled, useful for confirming our handler actually ran.
        result_text = page.locator("#result").text_content() or ""

        browser.close()
        return f"{captured_message!r} -> page reported: {result_text}"


def download_demo() -> Path:
    """Triggers a file download and saves it to disk."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://the-internet.herokuapp.com/download")

        # A download doesn't load like a normal page navigation, the
        # browser hands the file to your OS instead of rendering
        # anything. page.expect_download() works the same way
        # context.expect_page() did in Lesson 11: start listening BEFORE
        # the click that triggers it, to avoid a race where the download
        # starts before we're watching for it.
        # This demo page lists files uploaded by every visitor of the
        # public practice site, so most of the list changes constantly.
        # "sample.txt" is one of the site's own permanent fixtures, we
        # target it by name instead of just picking the first link, so
        # this lesson downloads the same real file every time it runs.
        with page.expect_download() as download_info:
            page.locator("a[href='download/sample.txt']").click()
        download = download_info.value

        # The download exists in a temporary location the instant it
        # starts; save_as() is what actually copies it somewhere we
        # control and can inspect afterward.
        saved_path = OUTPUT_DIR / download.suggested_filename
        download.save_as(saved_path)

        browser.close()
        return saved_path


def main() -> None:
    print("1. Handling a JavaScript alert dialog:")
    outcome = dialog_demo()
    print(f"   {outcome}")

    print("\n2. Triggering and saving a file download:")
    saved_path = download_demo()
    print(f"   Saved to: {saved_path}")
    print(f"   File size: {saved_path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
