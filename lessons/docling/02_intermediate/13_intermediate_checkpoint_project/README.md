# Lesson 13 (Intermediate checkpoint): table + OCR + chunked JSON pipeline

## No new API, just the pieces put together

Lessons 7-12 covered pipeline options, table structure, OCR, picture
extraction, chunking, and JSON export separately, one concept at a
time. This checkpoint runs the actual pipeline you'd build from those
pieces: convert two structurally different documents with one default
`DocumentConverter`, chunk each with `HybridChunker`, and write
everything out as one JSON file, source file, headings, and both the
raw and contextualized text for every chunk.

## Why these two specific files

`quarterly_report.pdf` has a real text layer and a table, it exercises
the table-structure path from Lesson 8. `scanned_invoice.pdf` has no
text layer at all, it exercises the OCR path from Lesson 9. Both
convert correctly with the exact same default `DocumentConverter()`,
no per-file configuration needed, `do_ocr` and `do_table_structure`
are on by default and each only does work where there's something for
it to do.

## The output shape

```python
{
    "source": filename,
    "headings": chunk.meta.headings,
    "text": chunk.text,
    "contextualized_text": chunker.contextualize(chunk=chunk),
}
```

This is close to the actual row shape you'd insert into a vector
store: `contextualized_text` is what gets embedded, `text` and
`headings` stay around as metadata for display and provenance. Lesson
18's capstone extends this exact shape into something queryable.

## Running it

```bash
uv run python lessons/docling/02_intermediate/13_intermediate_checkpoint_project/lesson.py
```

## Expected output

```
Converted 2 documents into 4 chunks
Wrote chunks.json (3,305 bytes)

[quarterly_report.pdf] ['Executive Summary']
  Executive Summary
Revenue grew across all three regions this quarter, led by the North region's expa
[quarterly_report.pdf] ['Revenue by Region']
  Revenue by Region
North, Product Line = Hardware. North, Q2 Revenue = $412,000. North, Q3 Revenue = 
[quarterly_report.pdf] ['Outlook']
  Outlook
Q4 guidance assumes the North region's new partners ramp to full volume by week six. Service
[scanned_invoice.pdf] None
  INVOICE#4471
Bill To Meridian Logistics Co. Date:2026-07-14
Item Qty Unit Price Total Warehouse pall
```

`scanned_invoice.pdf`'s single chunk has `headings: None`, that
document has no section headings at all (it's a flat invoice, not a
sectioned report), `HybridChunker` still chunks it correctly, there's
just nothing to attach to `.meta.headings`.

## Checkpoint

- **No new API**: this lesson is Lessons 8, 9, and 11 in one script,
  with default pipeline options doing the right thing for both a
  native-text and an image-only PDF.
- **One converter handles structurally different documents correctly**:
  `do_ocr` and `do_table_structure` only do work where there's
  something to find.
- **The chunk-to-JSON shape**: `source`, `headings`, `text`,
  `contextualized_text`, close to a real vector store insert.

You've finished the Intermediate tier. If anything here still feels
unclear, ask before moving to Lesson 14 and the Advanced tier.
