# Lesson 1: What is MarkItDown?

## The problem: LLMs read text, your files aren't text

An LLM prompt is a string. Almost nothing you actually need to feed it
starts out as a string: it's a `.docx` memo, a `.pptx` deck, an
`.xlsx` spreadsheet, a `.pdf` spec sheet, a `.png` screenshot, or a web
page. Before any of that can go into a prompt, into a RAG index, or
into a tool call, something has to turn it into text.

**MarkItDown** is Microsoft's open-source answer to that problem: a
Python library that converts a wide range of file formats into
Markdown. Not plain text, Markdown specifically, because Markdown
still carries structure an LLM can use: headings stay headings, tables
stay tables, list items stay list items. That structure is often the
difference between an LLM correctly answering "what's the third bullet
under Key Requirements" and it guessing.

## Where MarkItDown fits next to this repo's other converters

This repo also has a `liteparse` course. Both libraries turn documents
into text an LLM can consume, but they solve different problems:

| | MarkItDown (this course) | LiteParse (`lessons/liteparse/`) |
|---|---|---|
| Format coverage | Broad: docx, pptx, xlsx, pdf, images, audio, html, csv, zip, urls, and more | PDF only |
| What it optimizes for | Breadth, one converter for "whatever file just landed in my inbox" | Depth on PDFs specifically: layout fidelity, OCR, forms |
| Output | Markdown, generally simpler | Markdown/text, with more structural detail on complex PDFs |
| Typical use | Feeding varied source formats into an LLM or a RAG index | Feeding PDF-heavy pipelines where layout accuracy matters |

Neither replaces the other. If everything you handle is PDFs and you
need to catch every table cell and scanned page, LiteParse's narrower
focus pays off, that comparison is Lesson 11. If your input folder is
a mixed bag of office documents, images, and text files, and a
"probably right" Markdown conversion is enough, MarkItDown's breadth
is the better fit. This course assumes no prior exposure to either,
but Lessons 10 and 11 lean on basic familiarity with
[`lessons/llamaindex/`](../../../llamaindex/) (Lessons 1-4) and the
existence of [`lessons/liteparse/`](../../../liteparse/).

## Installing MarkItDown: the `[all]` extra matters

MarkItDown ships with format support split into optional extras, so
you only install what you need:

```bash
pip install markitdown            # base package: plain text, html, csv, zip, a handful of others
pip install markitdown[pdf]       # adds PDF support
pip install markitdown[docx]      # adds .docx support
pip install markitdown[pptx]      # adds .pptx support
pip install markitdown[xlsx]      # adds .xlsx support
pip install markitdown[all]       # every format extra, including pdf/docx/pptx/xlsx
```

If you install the bare package and try to convert a PDF, you don't
get a vague error, you get a `MissingDependencyException` that names
the exact extra you're missing. This project's `pyproject.toml`
already specifies `markitdown[all]`, and `uv sync` installed it, so
every format used in this course works out of the box. Nothing else
to install, no API key required for anything through Lesson 5, this
lesson's "Setup" section in the course [README](../../README.md) has
the full picture.

## The code, piece by piece

```python
version = importlib.metadata.version("markitdown")
```

Confirms the package is actually installed and reports its version,
the same idea as Lesson 1 of the Ollama course checking `ollama list()`
before assuming anything works.

```python
from markitdown import MarkItDown
md = MarkItDown()
```

Constructing `MarkItDown()` with no arguments registers every
built-in converter whose dependencies are satisfied. This succeeds
even without `markitdown[all]`, individual converters just wouldn't be
able to run yet, the `MissingDependencyException` only appears when
you actually try to `.convert()` an unsupported format.

## Running it

```bash
uv run python lessons/markitdown/01_beginner/01_what_is_markitdown/lesson.py
```

## Expected output

A `pydub` `RuntimeWarning` about `ffmpeg` appears first, that's
harmless here, `ffmpeg` isn't installed in this environment and this
course doesn't use audio transcription. The converter count depends on
the installed version, but with `markitdown[all]` it should be well
into the double digits:

```
MarkItDown (this course) vs LiteParse (lessons/liteparse/):
  Format coverage: Broad (docx, pptx, xlsx, pdf, images, html, csv, zip...) vs PDF only
  What it optimizes for: Breadth, one converter for many formats vs depth on PDF layout/OCR/forms
  Output: Markdown, generally simpler vs Markdown/text with more structural detail
  Typical use: Mixed source formats into an LLM or RAG index vs PDF-heavy pipelines needing layout accuracy

markitdown version installed: 0.1.5
MarkItDown() constructed successfully, ready to convert.
Converter count: 18
```

## Checkpoint

- **MarkItDown**: Microsoft's open-source library for converting many
  file formats into Markdown, aimed at feeding LLMs.
- **Why Markdown, not plain text**: it preserves structure (headings,
  tables, lists) that plain text loses, and that structure helps LLMs
  answer questions accurately.
- **MarkItDown vs LiteParse**: broad format coverage vs deep PDF-only
  fidelity, not a strictly-better-or-worse choice, full comparison in
  Lesson 11.
- **The `[all]` extra**: format support is opt-in via extras; without
  it, converting an unsupported format raises a
  `MissingDependencyException` naming what's missing. This project
  already has `markitdown[all]` installed.

If anything here still feels unclear, ask before moving to Lesson 2.
