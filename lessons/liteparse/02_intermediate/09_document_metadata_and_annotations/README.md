# Lesson 9: Document metadata, annotations, and links

## Three separate things, three separate options

This lesson turns on three independent options that are easy to
conflate:

| Option | What it adds | Where it lives |
|---|---|---|
| `extract_document_metadata` | Provenance facts about the file itself | `result.doc_meta` (document-level) |
| `extract_annotations` | PDF annotation objects on top of page content | `page.annotations` (page-level) |
| `extract_links` | Whether hyperlinks render as `[text](url)` in Markdown output | Affects `page.markdown` rendering only |

## `DocumentMetadata`: about the file, not the content

```python
parser = liteparse.LiteParse(extract_document_metadata=True, ...)
result = parser.parse(SAMPLE_PDF)
meta = result.doc_meta
```

`doc_meta` has nothing to do with what the document says. It's
provenance: `creation_date`/`mod_date` from the PDF's `/Info`
dictionary, `file_version` (an encoded integer, 14 means PDF 1.4),
`is_encrypted`, and `raw_file_size`. `result.creator` and
`result.producer` (not nested under `doc_meta`) report the authoring
tool: here, `producer` shows `"ReportLab PDF Library"`, the real
library used to generate this course's sample PDFs.

## `DocumentAnnotation`: content sitting on top of the page

```python
page = result.pages[0]
for annotation in page.annotations:
    ...
```

`vendor_memo.pdf` contains a real link annotation: the phrase
"Procurement Policy" is backed by a `link`-subtype annotation with a
`uri` (`https://example.com/procurement-policy`) and a `rect` in the
same top-left, 72-DPI coordinate space every other bounding box in this
course uses (`TextItem`, `FormField`, `ScreenshotRect`). Annotations
also cover comments, highlights, and stamps on richer PDFs, though this
sample only exercises the link case.

## `extract_links`: a rendering switch, not an extraction switch

`extract_links` (on by default) only matters when `output_format="markdown"`
(Lesson 3): it decides whether a hyperlink becomes Markdown syntax
(`[Procurement Policy](https://example.com/procurement-policy)`) or
stays as plain anchor text. It does **not** control whether the link
data itself is available, that's `extract_annotations`'s job. Plain
`result.text` never includes URLs inline either way; it just reads as
prose, as shown in the last line of this lesson's output.

## Running it

```bash
uv run python lessons/liteparse/02_intermediate/09_document_metadata_and_annotations/lesson.py
```

## Expected output

```
Document metadata (result.doc_meta):
  creation_date: D:20260809105147+01'00'
  file_version: 13 (14 would mean PDF 1.4)
  is_encrypted: False
  raw_file_size: 2048 bytes
  creator: 'anonymous'
  producer: 'ReportLab PDF Library - (opensource)'

Annotations on page 1 (1 found):
  subtype: link
  uri: https://example.com/procurement-policy
  rect: x=72, y=90, w=128, h=17

result.text still reads as plain prose, the link text is inline:
  'Vendor Memo: Northwind Supplies\n\nSee our procurement policy for details:\nProcurement Policy\n\n\nNote: pricing below is valid through the end of this quarter.\n\nItem: Recycled paper, Price: $4.20 per ream\nItem: Toner cartridge, Price: $38.00 each'
```

`creation_date` reflects when this course's fixture PDFs were built and
will differ if you regenerate them.

## Checkpoint

- `extract_document_metadata` gives you file provenance
  (`result.doc_meta`), not content.
- `extract_annotations` gives you page-scoped annotation objects
  (`page.annotations`), links, comments, highlights, each with a `rect`
  in the same coordinate space as other bounding boxes.
- `extract_links` only affects Markdown rendering of hyperlinks, it's a
  presentation switch, not an extraction switch.

If anything here still feels unclear, ask before moving to Lesson 10.
