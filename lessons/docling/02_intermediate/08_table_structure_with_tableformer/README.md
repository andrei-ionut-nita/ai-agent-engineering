# Lesson 8: table structure recognition with TableFormer

## The gap Markdown tables hide

`export_to_markdown()` has produced a clean pipe table for
`quarterly_report.pdf` since Lesson 2, but a Markdown table is still a
string, getting "the North/Hardware growth number" out of it means
re-parsing pipes and whitespace. TableFormer, docling's dedicated
table-structure model, already did the real work of understanding
rows, columns, and headers, `export_to_dataframe()` exposes that
structure directly as a pandas DataFrame, no re-parsing required.

## `TableFormerMode.FAST` vs `ACCURATE`

```python
from docling.datamodel.pipeline_options import TableFormerMode

options = PdfPipelineOptions()
options.table_structure_options.mode = TableFormerMode.ACCURATE  # the default
```

`ACCURATE` is what every earlier lesson has been using implicitly,
it's the default. `TableFormerMode.FAST` trades some structural
precision (particularly on tables with merged or spanning cells) for
speed, worth reaching for on a large batch of simple, regularly-shaped
tables where `ACCURATE`'s extra care doesn't change the outcome.

## `export_to_dataframe()`

```python
table = result.document.tables[0]
df = table.export_to_dataframe(result.document)
```

Recent docling versions want the owning `DoclingDocument` passed in
(a deprecation warning appears if you omit it), since a table item's
cell references are resolved against the document it belongs to. The
result is an ordinary pandas `DataFrame`: filter it, join it, feed it
to `pandas.read_sql`-shaped code, anything you'd do with tabular data
that didn't come from a PDF.

## Running it

```bash
uv run python lessons/docling/02_intermediate/08_table_structure_with_tableformer/lesson.py
```

## Expected output

```
TableFormer ACCURATE, as a DataFrame:
  Region Product Line Q2 Revenue Q3 Revenue  Growth
0  North     Hardware   $412,000   $498,000  +20.9%
1  North     Services   $188,000   $225,000  +19.7%
2  South     Hardware   $276,000   $291,000   +5.4%
3  South     Services   $142,000   $150,000   +5.6%
4   West     Hardware   $355,000   $402,000  +13.2%
5   West     Services   $201,000   $219,000   +9.0%

Shape: 6 rows x 5 columns

North / Hardware row:
Region Product Line Q2 Revenue Q3 Revenue Growth
 North     Hardware   $412,000   $498,000 +20.9%
```

## Checkpoint

- **TableFormer**: docling's dedicated table-structure model, the
  thing actually producing correct rows and columns, not just text in
  a grid-shaped region.
- **`TableFormerMode.ACCURATE` vs `FAST`**: `ACCURATE` is the default,
  `FAST` trades precision on complex tables for throughput.
- **`export_to_dataframe(doc)`**: a table's structure as a real pandas
  `DataFrame`, filterable and joinable, not a Markdown string to
  re-parse.

If anything here still feels unclear, ask before moving to Lesson 9.
