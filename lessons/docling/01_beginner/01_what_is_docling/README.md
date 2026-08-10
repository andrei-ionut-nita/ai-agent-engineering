# Lesson 1: What docling is, and why it exists

## The problem docling solves

Feeding a document to an LLM usually means turning it into text first.
For a `.txt` file that's trivial. For a real PDF report with a table,
a chart, and a two-column layout, it is not: the raw text extracted by
a naive PDF reader often comes out with headings mixed into body text,
table cells flattened into one unreadable line, and reading order
scrambled by columns. docling exists to solve that specific problem:
it runs a trained layout model over the page image, understands where
headings, paragraphs, tables, and pictures actually are, and produces
one clean structured document from that understanding.

## Where docling sits next to markitdown and liteparse

All three libraries answer "turn this document into something an LLM
can read", but they sit at different points on a fidelity-versus-speed
axis:

- **markitdown** optimizes for breadth and simplicity: the widest
  format coverage, a single `.convert()` call, minimal setup.
- **liteparse** optimizes for PDF fidelity at speed: layout, forms,
  and OCR, tuned to stay fast.
- **docling** goes deepest on structure: a real layout model, a
  dedicated table-structure model (TableFormer), OCR, and formula and
  code recognition, at the cost of heavier dependencies and slower
  conversions.

None of that makes docling strictly "better", it makes it the right
tool when structural fidelity (a table your code can actually read as
a table, not a wall of text) matters more than raw speed. Lesson 17
tests this claim directly once you've used all three enough to judge
for yourself.

## One converter, many formats

The core object is `DocumentConverter`. It needs no arguments to
construct, and no API key or network account, everything it does runs
locally:

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
```

`InputFormat` is the enum listing every format docling's backends know
how to read, PDF, DOCX, PPTX, HTML, images, and quite a few more. This
course mostly uses `pdf`, `docx`, and `pptx`, but the same
`DocumentConverter` handles all of them without any per-format setup
from you.

## Running it

```bash
uv run python lessons/docling/01_beginner/01_what_is_docling/lesson.py
```

## Expected output

```
docling supports 30 input formats:
  - asciidoc
  - audio
  - boxnote
  - csv
  - dclx
  - doc
  - docx
  - ebcdic
  - email
  - epub
  - html
  - image
  - json_docling
  - latex
  - md
  - mets_gbs
  - odp
  - ods
  - odt
  - pdf
  - ppt
  - pptx
  - video
  - vtt
  - xls
  - xlsx
  - xml_doclang
  - xml_jats
  - xml_uspto
  - xml_xbrl

This course focuses mainly on: pdf, docx, pptx.
DocumentConverter instance ready: <docling.document_converter.DocumentConverter object at 0x...>
```

(The exact set and count of formats can grow with newer docling
releases, that's fine, the memory address will always differ.)

## Checkpoint

- **docling**: an open-source document-conversion library built around
  a real layout model, not just text extraction.
- **`DocumentConverter`**: the single entry point, needs no arguments
  or API key to construct.
- **`InputFormat`**: the enum of every format docling's backends
  support, checked here, used directly starting Lesson 2.
- **The fidelity/speed axis**: markitdown (breadth, simplicity),
  liteparse (PDF fidelity, speed), docling (deepest structure, more
  setup and compute).

If anything here still feels unclear, ask before moving to Lesson 2.
