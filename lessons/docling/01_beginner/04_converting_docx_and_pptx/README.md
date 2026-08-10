# Lesson 4: one converter, many formats

## No format-specific setup

Lessons 1-3 only ever touched a PDF. This lesson runs the exact same
`DocumentConverter` instance over `project_plan.docx` and
`team_update.pptx` too, with no extra configuration, docling detects
the format from the file (extension, or content sniffing for a
stream) and routes it to the right backend automatically.

```python
converter = DocumentConverter()
for filename in ["quarterly_report.pdf", "project_plan.docx", "team_update.pptx"]:
    result = converter.convert(SAMPLE_DATA / filename)
```

This is the same pattern markitdown's course used for its own
multi-format lesson, one converter object, a loop over files, docling
just does more work per file to get there (a trained layout model for
PDF, versus reading DOCX/PPTX's own native structure directly, since
those formats already carry heading and paragraph information in
their XML).

## Why DOCX and PPTX convert with zero tables or pictures here

`project_plan.docx` and `team_update.pptx` are plain text and bullet
lists, this course's fixtures for those formats don't happen to
include an embedded table or image. That's not a limitation, docling
reads native tables and images from DOCX/PPTX just as well as it does
from PDF, this fixture set simply doesn't exercise that path. Lesson 8
(tables) and Lesson 10 (pictures) both work from `quarterly_report.pdf`
specifically because that's the fixture built with a table and a
picture.

## Running it

```bash
uv run python lessons/docling/01_beginner/04_converting_docx_and_pptx/lesson.py
```

## Expected output

```
quarterly_report.pdf
  format: InputFormat.PDF
  texts=13 tables=1 pictures=1
  first line: ## Q3 Regional Sales Report

project_plan.docx
  format: InputFormat.DOCX
  texts=11 tables=0 pictures=0
  first line: # Warehouse Automation Rollout

team_update.pptx
  format: InputFormat.PPTX
  texts=9 tables=0 pictures=0
  first line: # Warehouse Automation: Weekly Update
```

## Checkpoint

- **One `DocumentConverter`, many formats**: no per-format setup,
  format is detected from the file itself.
- **Backend differs by format under the hood**: PDF goes through a
  layout model, DOCX/PPTX read their own native XML structure, both
  end up as the same kind of `DoclingDocument`.
- **A top-level heading (`# Title`) versus a section header (`##
  Title`)**: DOCX's `Heading 0`/title style maps to a top-level
  heading in Markdown, distinct from the `section_header` labels seen
  on the PDF in Lesson 3.

If anything here still feels unclear, ask before moving to Lesson 5.
