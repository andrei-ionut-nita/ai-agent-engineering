# Lesson 3: what's actually inside a `DoclingDocument`

## Structure, not a string

Lesson 2 called `export_to_markdown()` and stopped there, a string was
enough for that lesson. But `result.document` is not a string, it's a
`DoclingDocument`, a real object graph: separate collections for text
items, tables, and pictures, each one a structured item with its own
label, not a character range you'd have to re-parse out of Markdown.
`export_to_markdown()` is one view onto that graph. This lesson looks
at the graph itself.

## The three collections

```python
doc.texts     # every paragraph, heading, list item, caption
doc.tables    # every detected table, as structured cells, not text
doc.pictures  # every detected figure or image region
```

Each collection holds items in the order docling's backend produced
them, not necessarily reading order, that's what `iterate_items()` is
for.

## Reading order with `iterate_items()`

```python
for item, level in doc.iterate_items():
    ...
```

This walks the whole document, texts, tables, and pictures together,
in the order a person would actually read the page: title first,
sections in sequence, a table where the table appears, not batched at
the end. `export_to_markdown()` calls this same method internally,
you're looking at exactly the traversal that produces the Markdown
output, just before it gets serialized to a string.

Every text item has a `.label` (`section_header`, `text`, and more
labels you'll see in later lessons like `list_item` and `caption`)
telling you what kind of text it is, this is the structural
information a plain PDF text extractor throws away.

## Running it

```bash
uv run python lessons/docling/01_beginner/03_the_docling_document/lesson.py
```

## Expected output

```
Text items:  13
Tables:      1
Pictures:    1

Reading order (label: text preview):
  section_header: Q3 Regional Sales Report
  section_header: Executive Summary
  text: Revenue grew across all three regions this quarter, led by t
  section_header: Revenue by Region
  table
  section_header: Regional Growth Chart
  picture
  section_header: Outlook
  text: Q4 guidance assumes the North region's new partners ramp to
```

## Checkpoint

- **`DoclingDocument`**: a structured object graph, not a string,
  `doc.texts`, `doc.tables`, `doc.pictures` hold real typed items.
- **`iterate_items()`**: walks the whole document in reading order,
  the same traversal `export_to_markdown()` uses internally.
- **`.label`**: every text item knows what kind of text it is
  (`section_header`, `text`, and more), structure a plain PDF text
  extractor would have discarded.

If anything here still feels unclear, ask before moving to Lesson 4.
