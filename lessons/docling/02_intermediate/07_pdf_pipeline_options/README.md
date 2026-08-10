# Lesson 7: `PdfPipelineOptions` and `format_options`

## Every prior lesson already had options, just defaults

`DocumentConverter()` with no arguments, used in every beginner
lesson, isn't option-free, it's running with `PdfPipelineOptions()`'s
defaults: OCR on, table structure recognition on. Those defaults are
why `quarterly_report.pdf`'s table showed up correctly in Lesson 3
without any configuration from you. This lesson makes that
configuration explicit, and shows what turning pieces of it off
actually costs and buys.

## Wiring options in through `format_options`

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

options = PdfPipelineOptions()
options.do_ocr = False
options.do_table_structure = False

converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
)
```

`format_options` is a dict keyed by `InputFormat`, this is also how
you'd hand different options to PDF versus, say, a future format that
takes its own `FormatOption` subclass. `PdfFormatOption` wraps a
`PdfPipelineOptions` instance specifically for the PDF pipeline.

## What `do_ocr=False` and `do_table_structure=False` change

Turning both off skips the two most expensive per-page models. On
`quarterly_report.pdf`, which already has a real text layer (it's a
generated, not scanned, PDF), `do_ocr=False` loses nothing: the text
layer is read directly either way, OCR only matters when there's no
text layer to read (Lesson 9). `do_table_structure=False` does change
something: a `table` item is still emitted from the PDF's own cell
grid, but without TableFormer reconciling merged cells and header
rows, so structure fidelity on a genuinely complex table would drop
even though a table object still exists.

## Running it

```bash
uv run python lessons/docling/02_intermediate/07_pdf_pipeline_options/lesson.py
```

## Expected output

Exact timings depend on your machine and whether model weights are
already cached locally, but the relative gap should reproduce: the
first conversion in this script pays for loading OCR and table
structure model weights, the second, run in the same warmed-up
process, skips both:

```
Default pipeline options: 15.67s
  tables detected: 1

do_ocr=False, do_table_structure=False: 0.52s
  tables detected: 1
  (a table item is still emitted from the PDF's own cell grid, just without TableFormer's structure model reconciling merged cells and headers)
```

## Checkpoint

- **`PdfPipelineOptions`**: the knobs controlling PDF-specific
  behavior, OCR, table structure recognition, and more in later
  lessons, `do_ocr=True` and `do_table_structure=True` by default.
- **`format_options={InputFormat.PDF: PdfFormatOption(...)}`**: how
  options get wired into a `DocumentConverter`, keyed by format.
- **Turning models off is a real speed lever**: mostly worth it when
  the source PDF already has a reliable native text layer.
- **A table item existing isn't the same as TableFormer having run**:
  disabling `do_table_structure` still yields a basic table object
  from the PDF's own grid, just without structure-model reconciliation.

If anything here still feels unclear, ask before moving to Lesson 8.
