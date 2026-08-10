# Lesson 9: OCR for scanned, image-only PDFs

## A fixture with no text layer

Every PDF used so far, `quarterly_report.pdf`, `research_note.pdf`,
had a real text layer: the PDF format itself stores the characters,
docling just reads them. `scanned_invoice.pdf` is different on
purpose, it's a picture of an invoice saved as a PDF, the same shape a
phone-camera photo or a flatbed scan produces. There is no text layer
at all, only pixels. This is exactly the case OCR exists for.

## Proving it with `do_ocr=False`

```python
options = PdfPipelineOptions()
options.do_ocr = False
```

Converting `scanned_invoice.pdf` with OCR turned off extracts nothing,
`export_to_text()` comes back empty. This isn't a bug, there's
genuinely no text for docling to read without recognizing it from the
image first.

## `do_ocr=True`, the default you've been using all along

Every prior lesson's `DocumentConverter()` already had `do_ocr=True`,
it just never mattered because those PDFs had text layers OCR wasn't
needed for. On `scanned_invoice.pdf`, it's the only thing that
produces output: docling's default OCR engine runs over the page
image, recognizes the characters, and inserts them back into the
document structure at the position they were found, so the recognized
text still participates in the same `DoclingDocument` structure as
text read from a native layer.

Recognized text from a real scan is rarely perfect (misread digits,
merged words), that's the nature of OCR, not a docling-specific
limitation. docling also supports pointing `ocr_options` at a specific
engine (EasyOCR is the default, Tesseract and RapidOCR are both
available as alternatives) when you need to match a particular
engine's accuracy or licensing profile, this lesson sticks to the
default to keep the comparison to exactly one variable: OCR on or off.

## Running it

```bash
uv run python lessons/docling/02_intermediate/09_ocr_for_scanned_pdfs/lesson.py
```

## Expected output

The exact character count can vary slightly by OCR engine version, the
overall shape (0 vs a few hundred characters, and roughly correct
invoice content) should reproduce:

```
do_ocr=False: extracted 0 characters

do_ocr=True (default): extracted 429 characters

INVOICE#4471

Bill To Meridian Logistics Co. Date:2026-07-14

Item Qty Unit Price Total Warehouse pallet racks 12 $340.00 $4,080.00 Freight handling 1 $650.00 $650.00 Installation labor 18 hrs $45.00 $810.00

Subtotal: $5,540.00 Tax (7%): $387.80 Total Due: $5,927.80

Payment terms Net30 days from invoice date.
```

Notice the OCR output isn't pixel-perfect (a missing space here, a
merged word there), that's genuinely how OCR works on real scans, not
something to over-trust for exact numeric extraction without a
human check.

## Checkpoint

- **Not every PDF has a text layer**: scanned or photographed pages
  are images, with nothing for a non-OCR reader to extract.
- **`do_ocr=True` is the default**: every earlier lesson already ran
  with OCR enabled, it just had nothing to do on PDFs with real text
  layers.
- **OCR output is approximate**: useful for search and rough
  extraction, not a substitute for verifying exact numbers by hand.
- **Multiple OCR engines are available**: EasyOCR by default, with
  Tesseract and RapidOCR as configurable alternatives via
  `ocr_options`.

If anything here still feels unclear, ask before moving to Lesson 10.
