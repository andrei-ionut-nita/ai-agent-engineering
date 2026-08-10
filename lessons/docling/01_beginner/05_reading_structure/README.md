# Lesson 5: reading structure, headings, sections, and plain text

## Pulling out just the outline

Lesson 3 iterated every item in reading order. Sometimes you don't
want every item, you want the document's outline: what are the
section headings, in order, with body text stripped out. Because
`doc.texts` items carry a `.label`, this is a filter, not a parser:

```python
from docling_core.types.doc import DocItemLabel

headings = [
    t for t in doc.texts
    if t.label in (DocItemLabel.TITLE, DocItemLabel.SECTION_HEADER)
]
```

`DocItemLabel` is the enum backing every `.label` value seen so far
(`title`, `section_header`, `text`, and more used in later lessons).
Importing it directly, instead of comparing against the raw string
`"section_header"`, keeps this code correct even if the underlying
string values ever change across docling versions.

## `export_to_text()`

`export_to_markdown()` produces Markdown syntax, `#` for headings, `|`
for tables. `export_to_text()` produces the same reading-order content
without any of that, just plain paragraphs and simple `- ` bullets.
Reach for it when the destination can't handle Markdown at all, an
older full-text search index, a plain log file, a system that would
choke on stray `#` characters.

## Running it

```bash
uv run python lessons/docling/01_beginner/05_reading_structure/lesson.py
```

## Expected output

```
Document outline:
  title: Warehouse Automation Rollout
  section_header: Phase 1: North Warehouse
  section_header: Phase 2: South and West Warehouses
  section_header: Risks

export_to_text() output:
Warehouse Automation Rollout

This plan covers the phased rollout of the new pick-and-pack automation across the three regional warehouses.

Phase 1: North Warehouse

Installation begins the first week of Q4, with staff training running in parallel during the second week.

- Conveyor belt replacement
- Barcode scanner upgrade
- Staff certification (2 days per shift)

Phase 2: South and West Warehouses

Rollout follows six weeks after North, once lessons learned from Phase 1 are folded into the installation checklist.

Risks

The main risk is parts lead time: conveyor motors currently run an eight week order-to-delivery window.
```

## Checkpoint

- **Filtering by `.label`**: pulling the outline out of a
  `DoclingDocument` is a list comprehension over `doc.texts`, not a
  regex or a Markdown parser.
- **`DocItemLabel`**: the enum backing every `.label`, safer to import
  and compare against than raw strings.
- **`export_to_text()`**: the same reading-order content as
  `export_to_markdown()`, without Markdown syntax, for destinations
  that can't handle `#` and `|`.

If anything here still feels unclear, ask before moving to Lesson 6.
