# Lesson 8: OCR for scanned documents

## The contrast this whole course has been building to

`scanned_notice.pdf` isn't a native-text PDF at all: it was built by
rendering a PNG image (`sample_data/_src/scanned_notice.png`) into a
PDF page. There is no PDF text layer in it, no `TextItem` LiteParse
could ever find by reading PDF text objects, because none exist. To a
computer, without OCR, it's just a picture. This is the exact situation
`ocr_enabled` (mentioned since Lesson 2) exists for.

## `ocr_enabled=False`: nothing to extract

With OCR off, LiteParse only reads native PDF text objects. This page
has zero of them, so the result is an empty string, correctly: there
really is no extractable native text on this page, no matter how
obviously readable the notice is to a human looking at it.

## `ocr_enabled=True`: renders the page, runs Tesseract

With OCR on (the default), LiteParse's complexity heuristics recognize
this page needs more than the native-text path: no native text and a
full-page embedded image is exactly the signature of a scan. It renders
the page to a bitmap and runs Tesseract OCR against that bitmap,
recovering real, readable text: "NOTICE... Building maintenance will
occur on Saturday... Water service will be interrupted from 9 AM to 1
PM..." The OCR text isn't pixel-perfect (spacing and line breaks don't
exactly match the source image), but the words are all there and
correct.

## `is_complex()`: seeing the decision, not just the result

```python
stats = parser.is_complex(SCANNED_PDF)
```

`is_complex()` runs the same cheap pre-check LiteParse's own OCR
decision is based on, without doing a full parse. On this page it
reports `needs_ocr=True` with reasons `['no-text', 'embedded-images']`:
zero native text characters, and a page that's essentially a picture.
This is useful on its own, as a fast way to triage a folder of PDFs
into "needs OCR" and "doesn't" before committing to a full (slower)
OCR parse of everything. Lesson 11's checkpoint project builds exactly
that triage step, though it also shows a case where `needs_ocr` fires
on a page that already has perfectly good native text, so it's a signal
to weigh, not a rule to follow blindly.

## Running it

```bash
uv run python lessons/liteparse/02_intermediate/08_ocr_for_scanned_documents/lesson.py
```

## Expected output

```
ocr_enabled=False:
  characters extracted: 0
  text: ''

ocr_enabled=True:
  characters extracted: 183
  text: '    NOTICE\n\n\nBuilding maintenance will occur on Saturday.\nWater service will be interrupted from 9 AM to 1 PM.\n\nPlease plan accordingly and contact the front\n\ndesk with any questions.'

is_complex() verdict for page 1:
  needs_ocr: True
  reasons: ['no-text', 'embedded-images']
  text_length (native): 0
  full_page_image: False
```

OCR output text is deterministic here (Tesseract on a clean, static
rendered image), but if you re-run this on a different machine with a
different Tesseract version, minor whitespace differences are possible.

## Checkpoint

- Native PDF text and OCR-recovered text are fundamentally different
  sources; a scanned page has zero of the former.
- `ocr_enabled=False` never attempts OCR, even on a page that clearly
  needs it.
- `ocr_enabled=True` (the default) uses complexity heuristics to decide
  per page whether OCR is worth running, and runs Tesseract when it is.
- `is_complex()` exposes that same verdict cheaply, without a full
  parse, useful for triaging a batch before committing to OCR.

If anything here still feels unclear, ask before moving to Lesson 9.
