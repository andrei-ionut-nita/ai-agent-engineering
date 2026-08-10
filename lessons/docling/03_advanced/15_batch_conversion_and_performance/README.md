# Lesson 15: batch conversion and reusing one converter

## One converter, many files

Every earlier lesson constructed a fresh `DocumentConverter()` inside
`main()`, that's the right shape for a single-file example. It is not
the right shape for a real batch job: constructing a converter isn't
free, its pipelines load model weights the first time each is used.
Lesson 6's checkpoint already reused one converter across a loop, this
lesson names the pattern explicitly and uses `convert_all()`, docling's
built-in batch entry point, instead of writing the loop by hand.

```python
converter = DocumentConverter()
results = list(converter.convert_all([path1, path2, path3, ...]))
```

`convert_all()` takes any iterable of sources (paths, URLs, or
`DocumentStream`s, mixed formats included) and returns an iterator of
`ConversionResult`s, one per source, in order. It's functionally
equivalent to calling `.convert()` in a loop, the value is that it's
the documented, idiomatic entry point for "convert several things",
so it's what to reach for instead of writing the loop yourself.

## Why reuse actually matters here

This lesson converts four structurally different files (a PDF with a
table, a DOCX, a PPTX, another PDF) with one `DocumentConverter`. Every
one of them shares the same underlying layout and table-structure
models where applicable, format-specific backends (DOCX, PPTX) don't
load PDF-specific models at all, and PDF-specific models only get
initialized once, not once per PDF. Constructing a new converter per
file would repeat that initialization cost for no benefit, the models
themselves don't change between files.

## Running it

```bash
uv run python lessons/docling/03_advanced/15_batch_conversion_and_performance/lesson.py
```

## Expected output

Exact timing depends on your machine and whether model weights are
already cached:

```
Converted 4 files with one reused converter in 16.84s

  quarterly_report.pdf     ConversionStatus.SUCCESS  texts=13
  project_plan.docx        ConversionStatus.SUCCESS  texts=11
  team_update.pptx         ConversionStatus.SUCCESS  texts=9
  research_note.pdf        ConversionStatus.SUCCESS  texts=5

Compare this to constructing a new DocumentConverter() per file: each one would re-check model availability and re-initialize pipelines, even though the same underlying weights end up loaded either way. One converter, many files, is the right shape for a batch job.
```

## Checkpoint

- **`convert_all(sources)`**: docling's built-in batch entry point,
  takes any iterable of paths/URLs/streams, returns an iterator of
  `ConversionResult`s.
- **Construct one `DocumentConverter`, not one per file**: model
  initialization cost is paid once, not repeated per document.
- **Mixed formats in one batch are fine**: `convert_all()` doesn't
  require every source to share a format.

If anything here still feels unclear, ask before moving to Lesson 16.
