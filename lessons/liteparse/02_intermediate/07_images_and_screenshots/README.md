# Lesson 7: Images and screenshots

## Two unrelated meanings of "image"

`extract_images` pulls raster images **out of** a PDF: photos, logos,
scanned figures that exist as actual embedded image objects inside an
otherwise text-based document. `screenshot()` does the opposite: it
renders a whole page **into** a picture, a PNG of what the page looks
like, whether or not the page has any embedded images at all. These are
two separate features that happen to share the word "image."

## `extract_images`: this course's PDFs have none, correctly

Every sample PDF in this course was built from plain text (see
`sample_data/_src/`), so none of them contain an embedded raster image
object. `extract_images=True` correctly returns an empty `result.images`
list, not an error, that's the expected, correct answer for a document
that genuinely has no embedded images, not a sign anything is broken.
On a PDF that does contain embedded photos or logos, each one comes
back as an `ExtractedImage`: id, page, bounding box, pixel dimensions,
format, and raw bytes (plus a file path if `image_output_dir` was also
set).

## `screenshot()`: rendering a page as a picture

```python
lp = liteparse.LiteParse(quiet=True, detect_screenshot_rects=True)
shots = lp.screenshot(SAMPLE_PDF)
```

`screenshot()` is a separate method on `LiteParse`, not something
`.parse()` returns. It renders each page (or specific `page_numbers`)
to a `ScreenshotResult`: `width`/`height` in pixels, raw `image_bytes`
(PNG), and `is_solid_fill` (true if the whole render came back one flat
color, a quick "is this page actually blank" check).

## `detect_screenshot_rects`: useful, but read the numbers honestly

With `detect_screenshot_rects=True`, `screenshot()` also scans the
rendered bitmap for solid rectangles and lines, aimed at design elements
that only exist as pixels, not as PDF objects: colored callout boxes,
ruled table borders, section dividers. On `intake_form.pdf`, a page
that's almost entirely plain text, it returned **353 rectangles**, and
every single one of them turned out to be a thin line. Looking at the
actual detections, they're the individual vertical/horizontal strokes
of rendered letters at high DPI, not table borders or design boxes.
Filtering to a minimum area of 200pt² throws out all 353, correctly,
since none of them represent a real graphical element on this page.

The lesson here isn't that the feature is broken, it's that it's
answering the question "what solid-colored regions exist in this
bitmap," and a text-heavy page has plenty of those at the glyph level.
On a document with actual colored boxes or ruled tables, the same
filter would keep the real ones and drop the noise. Always filter by
size (and often by aspect ratio) before treating `detect_screenshot_rects`
output as a table/box detector.

## Running it

```bash
uv run python lessons/liteparse/02_intermediate/07_images_and_screenshots/lesson.py
```

## Expected output

```
extract_images=True on lessons/liteparse/sample_data/intake_form.pdf: 0 embedded image(s) found
  (none of this course's sample PDFs contain an embedded raster image, they were built from plain text, so 0 is the correct, expected answer here, not a failure.)

screenshot() page 1: 1275x1650px, 92750 bytes (PNG)
  saved to: /tmp/liteparse_lesson07__6mjc6s0/intake_form_page1.png

detect_screenshot_rects found 353 rect(s) total
  353 are thin lines (mostly glyph stroke edges on a text-heavy page)
  0 are filled areas
  0 remain after filtering to area >= 200pt^2

  Takeaway: detect_screenshot_rects is built for documents with real graphical elements (colored boxes, ruled tables, dividers), not plain text pages, where it mostly rediscovers the font rendering. Always filter by size before trusting it as a table/box detector.
```

The temp file path will differ on your machine each run.

## Checkpoint

- `extract_images`: pulls embedded raster image objects out of a PDF;
  an empty result on a text-only PDF is correct, not a failure.
- `screenshot()`: a separate method that renders a whole page to a PNG,
  independent of whether the page has embedded images.
- `detect_screenshot_rects`: finds solid rectangles/lines in the
  rendered bitmap, but on plain text pages most detections are glyph
  strokes, always filter by size before trusting the output.

If anything here still feels unclear, ask before moving to Lesson 8.
