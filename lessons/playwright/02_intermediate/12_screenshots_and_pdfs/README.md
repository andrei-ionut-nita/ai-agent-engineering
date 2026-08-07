# Lesson 12: Screenshots and PDFs

## When text isn't enough

Every lesson so far has extracted text: a title, a price, a link. But
sometimes you need a visual artifact instead: a screenshot to prove
what an agent actually saw at a given moment (useful for debugging a
scraper that suddenly breaks), or a PDF as a shareable, print-style
record of a page. Playwright can produce both directly, no separate
screenshot tool or PDF library needed.

## The code, piece by piece

```python
OUTPUT_DIR = Path(__file__).parent / "output"
```

`Path(__file__)` is this very script's own location on disk;
`.parent` is the folder containing it. Building paths this way means
the lesson always writes its output next to itself, no matter what
folder you happened to run the command from.

```python
page.screenshot(path=viewport_path)
```

Captures exactly what's visible in the browser's viewport (the visible
window area) at that moment, nothing that would require scrolling to
see. This is the fast, default option.

```python
page.screenshot(path=full_page_path, full_page=True)
```

`full_page=True` instead scrolls through the entire page and stitches
everything into one tall image, capturing content below the fold too.
It costs a bit more time, since Playwright has to render and capture
the whole page rather than just the current viewport.

```python
page.pdf(path=pdf_path, format="A4")
```

Generates a PDF the same way a browser's own "Print to PDF" feature
would. This only works in **headless** Chromium (no visible window,
which is the default when you call `p.chromium.launch()` without
`headless=False`), and it's Chromium-specific, not every browser
engine implements PDF export. `format="A4"` sets the paper size, the
same setting you'd see in a real print dialog.

## Running it

```bash
uv run python lessons/playwright/02_intermediate/12_screenshots_and_pdfs/lesson.py
```

This writes three files into an `output/` folder next to this lesson:
`viewport.png`, `full_page.png`, and `page.pdf`. Open them to see what
was actually captured.

## Expected output

```
1. Screenshots:
   Viewport screenshot saved to: .../12_screenshots_and_pdfs/output/viewport.png
   Full-page screenshot saved to: .../12_screenshots_and_pdfs/output/full_page.png
   Viewport file size: 41213 bytes
   Full-page file size: 198442 bytes

2. PDF:
   PDF saved to: .../12_screenshots_and_pdfs/output/page.pdf
   PDF file size: 33982 bytes
```

Exact byte counts will vary, the site's content can change over time.

## Checkpoint

- **Viewport screenshot**: captures only what's currently visible on
  screen, fast, the default with `page.screenshot()`.
- **`full_page=True`**: scrolls through and captures the entire page,
  including content below the fold, slower but complete.
- **`page.pdf()`**: renders the page to a PDF, using the browser's own
  print engine. Headless Chromium only.
- **`Path(__file__).parent`**: a reliable way to build a path relative
  to the script's own location, independent of your terminal's current
  directory.

If anything here still feels unclear, ask before moving to Lesson 13.
