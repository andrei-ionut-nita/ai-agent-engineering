# Lesson 6 (Beginner checkpoint): convert a whole folder

## No new API, just the loop

This lesson doesn't introduce anything new from docling's side, it's
the checkpoint: prove Lessons 1-5 add up to something useful by
converting several mixed-format files with the same `.convert(path)`
call, one iteration per file, writing real `.md` files to disk plus a
small summary table of what structure was found in each.

This is close to the actual shape of a real ingestion script: point it
at a folder, convert what's there, get Markdown out the other side,
ready to chunk, embed, or feed straight into a prompt, the same
starting point the intermediate tier builds on.

## Why only three of the five sample files

`sample_data/` has five files, this checkpoint only converts three:
`quarterly_report.pdf`, `project_plan.docx`, `team_update.pptx`.
`scanned_invoice.pdf` (an image-only, no-text-layer PDF) and
`research_note.pdf` (built for formula/code enrichment) are left out
on purpose, both need pipeline options this course hasn't covered yet.
`scanned_invoice.pdf` comes back in Lesson 9 once OCR is introduced,
`research_note.pdf` comes back in Lesson 14.

## Running it

```bash
uv run python lessons/docling/01_beginner/06_beginner_checkpoint_project/lesson.py
```

## Expected output

```
Converted 3 files from sample_data/ into /home/nolan/Documents/Projects/ai-agent-engineering/lessons/docling/01_beginner/06_beginner_checkpoint_project/converted

Source file             Format    Texts   Tables  Pictures
----------------------------------------------------------
quarterly_report.pdf    .pdf      13      1       1
project_plan.docx       .docx     11      0       0
team_update.pptx        .pptx     9       0       0
```

(The absolute path in the first line will differ on your machine.) A
`converted/` subfolder now exists alongside this README, with three
`.md` files in it, open one and compare it to its source fixture.

## Checkpoint

- **No new API**: this lesson is Lessons 1-4's `.convert(path)`, in a
  loop, over several files.
- **Batch conversion shape**: list files, convert each, write output,
  track a summary, this is the skeleton of a real ingestion script.
- **Not every fixture is ready yet**: `scanned_invoice.pdf` needs OCR
  (Lesson 9), `research_note.pdf` needs enrichment options (Lesson
  14), both wait until this course covers the options that make them
  worth converting.

You've finished the Beginner tier. If anything here still feels
unclear, ask before moving to Lesson 7 and the Intermediate tier.
