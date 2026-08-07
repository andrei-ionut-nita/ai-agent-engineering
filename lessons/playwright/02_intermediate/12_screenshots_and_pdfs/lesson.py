"""
Lesson 12: screenshots and PDFs.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/02_intermediate/12_screenshots_and_pdfs/lesson.py

Every previous lesson pulled text out of a page. Sometimes what you
actually want is a picture of the page, or a print-style document of
it, useful for reports, visual debugging, or handing a human a record
of what an agent saw. This lesson covers both.
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

# All output files land in an "output" folder next to this lesson, so
# it's obvious where to look, and easy to delete afterward without
# touching anything else in the repo.
OUTPUT_DIR = Path(__file__).parent / "output"


def screenshot_demo(url: str) -> tuple[Path, Path]:
    """Takes a viewport-only screenshot and a full-page screenshot."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        # A plain screenshot captures only what's currently visible in
        # the viewport (the browser window's visible area), exactly like
        # a human pressing a screenshot key would see, nothing below the
        # fold.
        viewport_path = OUTPUT_DIR / "viewport.png"
        page.screenshot(path=viewport_path)

        # full_page=True instead scrolls through the ENTIRE page and
        # stitches it into one tall image, including everything below
        # the fold. Useful for a complete visual record, but the file is
        # bigger and it takes a moment longer, since Playwright has to
        # render the whole page, not just what's on screen.
        full_page_path = OUTPUT_DIR / "full_page.png"
        page.screenshot(path=full_page_path, full_page=True)

        browser.close()
        return viewport_path, full_page_path


def pdf_demo(url: str) -> Path:
    """Saves the page as a PDF, print-style."""
    with sync_playwright() as p:
        # PDF generation only works in headless mode, which is the
        # default for chromium.launch() (no headless=False here), and
        # only in Chromium, not every browser engine supports it. This
        # matches how a "print to PDF" button in a real browser works:
        # it's the browser's print engine doing the work, not a separate
        # library.
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        pdf_path = OUTPUT_DIR / "page.pdf"
        page.pdf(path=pdf_path, format="A4")

        browser.close()
        return pdf_path


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    url = "https://books.toscrape.com/"

    print("1. Screenshots:")
    viewport_path, full_page_path = screenshot_demo(url)
    print(f"   Viewport screenshot saved to: {viewport_path}")
    print(f"   Full-page screenshot saved to: {full_page_path}")
    print(f"   Viewport file size: {viewport_path.stat().st_size} bytes")
    print(f"   Full-page file size: {full_page_path.stat().st_size} bytes")

    print("\n2. PDF:")
    pdf_path = pdf_demo(url)
    print(f"   PDF saved to: {pdf_path}")
    print(f"   PDF file size: {pdf_path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
