"""
Lesson 7: extract_images, ExtractedImage, and screenshot()/detect_screenshot_rects.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/liteparse/02_intermediate/07_images_and_screenshots/lesson.py

Two different things both get called "images" in LiteParse's API:
embedded raster images that already exist as objects inside the PDF
(extract_images), and a screenshot LiteParse renders of a whole page as
a picture (screenshot()). This lesson covers both, including an honest
look at what detect_screenshot_rects actually returns on a plain text
page.
"""

import tempfile
from pathlib import Path

import liteparse

SAMPLE_PDF = "lessons/liteparse/sample_data/intake_form.pdf"


def main() -> None:
    # extract_images=True walks the PDF looking for embedded raster
    # image objects (photos, logos, scanned figures pasted into an
    # otherwise native-text document) and returns them as ExtractedImage,
    # with bytes, size, and page placement.
    parser = liteparse.LiteParse(ocr_enabled=False, quiet=True, extract_images=True)
    result = parser.parse(SAMPLE_PDF)
    print(f"extract_images=True on {SAMPLE_PDF}: {len(result.images)} embedded image(s) found")
    print(
        "  (none of this course's sample PDFs contain an embedded raster "
        "image, they were built from plain text, so 0 is the correct, "
        "expected answer here, not a failure.)\n"
    )

    # screenshot() is unrelated to extract_images: instead of pulling
    # images OUT of the PDF, it renders a whole page INTO one, a PNG
    # picture of what the page looks like, the same idea as a browser
    # screenshot. Useful for visual review, thumbnails, or feeding a
    # vision-capable model a page as a picture instead of text.
    lp = liteparse.LiteParse(quiet=True, detect_screenshot_rects=True)
    shots = lp.screenshot(SAMPLE_PDF)
    shot = shots[0]
    print(f"screenshot() page {shot.page_num}: {shot.width}x{shot.height}px, {len(shot.image_bytes)} bytes (PNG)")

    output_dir = Path(tempfile.mkdtemp(prefix="liteparse_lesson07_"))
    output_path = output_dir / "intake_form_page1.png"
    output_path.write_bytes(shot.image_bytes)
    print(f"  saved to: {output_path}")

    # detect_screenshot_rects=True additionally scans the rendered
    # bitmap for solid rectangles and lines, meant to catch design
    # elements (colored boxes, table borders, dividers) that don't exist
    # as PDF objects, only as pixels. On a plain text page like this
    # intake form, most of what it finds is NOT a meaningful design
    # element, it's the individual strokes of rendered letters, tiny,
    # numerous, and all flagged as is_line=True. Filtering to only
    # reasonably sized rectangles shows how much of the raw list is noise.
    print(f"\ndetect_screenshot_rects found {len(shot.rects)} rect(s) total")
    lines = [r for r in shot.rects if r.is_line]
    filled = [r for r in shot.rects if not r.is_line]
    print(f"  {len(lines)} are thin lines (mostly glyph stroke edges on a text-heavy page)")
    print(f"  {len(filled)} are filled areas")

    MIN_AREA = 200.0  # points^2, a rough floor to filter out glyph-stroke noise
    meaningful = [r for r in shot.rects if r.width * r.height >= MIN_AREA]
    print(f"  {len(meaningful)} remain after filtering to area >= {MIN_AREA:.0f}pt^2")
    print(
        "\n  Takeaway: detect_screenshot_rects is built for documents with "
        "real graphical elements (colored boxes, ruled tables, dividers), "
        "not plain text pages, where it mostly rediscovers the font "
        "rendering. Always filter by size before trusting it as a table/box "
        "detector."
    )


if __name__ == "__main__":
    main()
