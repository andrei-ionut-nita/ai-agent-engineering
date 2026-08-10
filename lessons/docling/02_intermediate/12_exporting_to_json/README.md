# Lesson 12: exporting to JSON, and loading it back

## The full structure, not a summary

`export_to_markdown()` and `export_to_text()` both throw information
away on purpose, bounding boxes, page numbers, provenance, none of
that survives into a Markdown string. `export_to_dict()` doesn't throw
anything away: it's the complete `DoclingDocument` structure, texts,
tables, pictures, groups, and page-level metadata, as plain Python
dicts and lists, ready for `json.dumps()`.

```python
as_dict = doc.export_to_dict()
Path("out.json").write_text(json.dumps(as_dict, indent=2))
```

## Why this matters for a real pipeline

Running the layout, table-structure, and OCR models is the expensive
part of a docling conversion, seconds per document, sometimes more.
`export_to_dict()` is what lets you pay that cost once: convert a
document, persist the JSON, and every later step (re-rendering to
Markdown, pulling a table out, re-chunking with different settings)
works off the cached JSON instead of re-running the pipeline.

## Loading it back with `DoclingDocument.model_validate()`

```python
from docling_core.types.doc.document import DoclingDocument

reloaded = DoclingDocument.model_validate(as_dict)
```

`DoclingDocument` is a Pydantic model, `model_validate()` is Pydantic's
standard "build a model instance from a dict" method. The reloaded
document is a real `DoclingDocument`, every method used in this course
so far, `export_to_markdown()`, `.tables[0].export_to_dataframe()`,
`HybridChunker().chunk()`, works on it identically to the object that
came straight out of `converter.convert()`.

## Running it

```bash
uv run python lessons/docling/02_intermediate/12_exporting_to_json/lesson.py
```

## Expected output

```
Top-level keys: ['body', 'form_items', 'furniture', 'groups', 'key_value_items', 'name', 'origin', 'pages', 'pictures', 'schema_name', 'tables', 'texts', 'version']
Schema: DoclingDocument v1.10.0
Wrote 54,115 bytes to quarterly_report.docling.json

Reloaded document: 13 texts, 1 tables
Original document:  13 texts, 1 tables

Reloaded document's markdown export (first 100 chars):
## Q3 Regional Sales Report

## Executive Summary

Revenue grew across all three regions this quarte
```

(Byte counts and the exact schema version can shift slightly across
docling releases, that's expected.)

## Checkpoint

- **`export_to_dict()`**: the complete, lossless `DoclingDocument`
  structure as plain Python data, unlike the Markdown/text exports.
- **Why cache it**: the layout/table/OCR models are the expensive part
  of a conversion, JSON lets you pay that cost once and re-derive any
  other export later.
- **`DoclingDocument.model_validate(d)`**: rebuilds a fully working
  `DoclingDocument` from the dict, every export method works the same
  as on the original.

If anything here still feels unclear, ask before moving to Lesson 13.
