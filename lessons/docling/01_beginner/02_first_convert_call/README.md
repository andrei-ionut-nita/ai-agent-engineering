# Lesson 2: your first `.convert()` call

## From folder to `ConversionResult`

Lesson 1 built a `DocumentConverter` but never fed it anything. This
lesson does that, on `sample_data/quarterly_report.pdf`, a two-page
PDF with headings, a table, and a chart image, generated for this
course and used again in several later lessons.

```python
converter = DocumentConverter()
result = converter.convert(SAMPLE_DATA / "quarterly_report.pdf")
```

`convert()` accepts a path, a URL string, or a `DocumentStream` for
in-memory bytes (that last one shows up in Lesson 9's OCR work). It
returns a `ConversionResult`, not a document directly, that result
carries a `.status` (did the conversion succeed), `.input` (what
format was detected), `.pages` (per-page metadata), and `.document`,
the actual `DoclingDocument`.

## `export_to_markdown()`

`result.document` is a `DoclingDocument`, docling's unified in-memory
representation, texts, tables, and pictures as structured objects, not
a string. `export_to_markdown()` walks that structure and serializes
it: headings become `#`/`##`, a detected table becomes a Markdown pipe
table, a detected picture becomes an `![]()` placeholder. This is the
method you'll reach for most often in this course, it's the fastest
path from "a document" to "text an LLM can read".

## Running it

```bash
uv run python lessons/docling/01_beginner/02_first_convert_call/lesson.py
```

## Expected output

```
Conversion status: ConversionStatus.SUCCESS
Input format detected: InputFormat.PDF
Page count: 2

First 500 characters of the converted Markdown:
## Q3 Regional Sales Report

## Executive Summary

Revenue grew across all three regions this quarter, led by the North region's expansion into two new distribution partners. The table below breaks results down by region and product line.

## Revenue by Region

| Region   | Product Line   | Q2 Revenue   | Q3 Revenue   | Growth   |
|----------|----------------|--------------|--------------|----------|
| North    | Hardware       | $412,000     | $498,000     | +20.9%   |
| North    | Services       | $188,000     | $225,000     | +2
```

The first run of this lesson on a fresh machine takes noticeably
longer, docling downloads its layout and table-structure model weights
the first time they're used, then caches them locally for every run
after that.

## Checkpoint

- **`convert()`**: takes a path, URL, or `DocumentStream`, returns a
  `ConversionResult`.
- **`ConversionResult`**: `.status`, `.input`, `.pages`, `.document`.
- **`.document`**: a `DoclingDocument`, docling's structured
  representation, not a plain string.
- **`export_to_markdown()`**: serializes that structure to Markdown,
  headings, tables, and picture placeholders included.

If anything here still feels unclear, ask before moving to Lesson 3.
