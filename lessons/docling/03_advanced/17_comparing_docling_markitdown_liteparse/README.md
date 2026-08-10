# Lesson 17: comparing docling, markitdown, and liteparse

## Testing Lesson 1's claim, not just repeating it

Lesson 1 laid out the fidelity/speed axis: markitdown trades PDF
structural depth for breadth and simplicity, liteparse trades some of
that depth for speed with real layout awareness, docling goes deepest
on structure at the cost of being the slowest of the three. That was a
claim, made before any of them had actually been run side by side.
This lesson runs all three on the same file, `quarterly_report.pdf`
(the fixture with a real table, used throughout this course), and
reports what actually happened.

## What the run found

On raw character count, all three produced similar-length output
(markitdown 930 chars, liteparse 894, docling 1063). Where they
genuinely diverged is what happened to the table's header row:

```
markitdown: | Region Product Line | Q2 Revenue | Q3 Revenue | Growth |
liteparse:  Region | Product Line   Q2 Revenue   Q3 Revenue | Growth
docling:    7 rows x 5 columns (Region and Product Line kept as separate columns)
```

markitdown and liteparse both read the PDF's raw text stream, which
records characters and their positions but has no concept of "this is
a table column boundary". Both merged the `Region` and `Product Line`
columns into one field, `Q2 Revenue` and `Q3 Revenue` fared better
mostly by luck of column spacing. docling's TableFormer model does
have that concept, it output a clean 7-row (1 header + 6 data) by
5-column table with every column correctly separated, matching Lesson
8's `export_to_dataframe()` output exactly.

Speed moved in the opposite direction: markitdown finished in about
0.05 seconds, liteparse in about 0.8 seconds, docling in roughly 15
seconds. That gap is the direct cost of the model docling ran to get
the table right, a real layout model plus TableFormer, versus reading
a text stream directly.

## The tradeoff, confirmed

This single fixture can't test every dimension (liteparse's OCR and
form-field handling, or markitdown's much broader format coverage,
aren't exercised here), but on the one thing this course's fixture is
built to test, table structure, the result matches the claim exactly:
docling is slower, and it is the only one of the three that got the
table right. Whether that tradeoff is worth it depends entirely on
what you're building: a one-off text extraction for a search index
probably doesn't need TableFormer, a pipeline that hands table data to
code expecting real rows and columns probably does.

## Running it

```bash
uv run python lessons/docling/03_advanced/17_comparing_docling_markitdown_liteparse/lesson.py
```

## Expected output

Timings will vary by machine and by whether docling's model weights
are already cached, the table-structure gap should reproduce:

```
Comparing conversions of: quarterly_report.pdf

=== markitdown ===
Q3 Regional Sales Report
Executive Summary
...
(markitdown: 930 chars, 0.049s)

=== liteparse ===
                        Q3 Regional Sales Report
Executive Summary
...
(liteparse: 894 chars, 0.788s)

=== docling ===
## Q3 Regional Sales Report

## Executive Summary
...
(docling: 1063 chars, 15.462s, tables detected: 1)

=== Observations ===
markitdown header row: '| Region Product Line | Q2 Revenue | Q3 Revenue | Growth |'
liteparse header row:  'Region | Product Line   Q2 Revenue   Q3 Revenue | Growth'
docling table shape:   7 rows x 5 columns (Region and Product Line kept as separate columns)
```

(liteparse also prints its own `[liteparse] ...` timing log lines
directly to stdout as it runs, that's liteparse's own instrumentation,
not something this lesson adds.)

## Checkpoint

- **Character count alone doesn't reveal fidelity**: all three
  produced similarly-sized output on this file, only inspecting the
  table structure showed the real difference.
- **markitdown and liteparse read a text stream, no table-boundary
  model**: adjacent table columns can merge when there's no model
  deciding where one ends and the next begins.
- **docling's TableFormer got the table exactly right**: a genuine
  fidelity advantage, at roughly 20-300x the wall-clock cost on this
  file.
- **The right tool depends on what downstream code expects**: text for
  a search index tolerates a merged column, code expecting real rows
  and columns does not.

If anything here still feels unclear, ask before moving to Lesson 18.
