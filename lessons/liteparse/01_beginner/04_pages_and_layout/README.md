# Lesson 4: Pages and layout

## `.text` is flattened; `.pages` is not

`result.text` (Lesson 2) is every page's text joined into one string, in
reading order, with page boundaries thrown away. That's fine when you
don't care which page a sentence came from. The moment you do, page
numbers for citations, per-page chunking for a vector index, skipping a
known-bad page, you need `result.pages` instead.

## `ParsedPage`, field by field

Each entry in `result.pages` is a `ParsedPage`:

| Field | What it is |
|---|---|
| `page_num` | 1-indexed page number |
| `width`, `height` | Page size in points (72 points = 1 inch; 595x842 is A4) |
| `text` | This page's own text, the slice `result.text` is built from |
| `text_items` | A list of `TextItem`, one per run of text, each with its own bounding box and font |
| `markdown` | Populated only with `output_format="markdown"` (Lesson 3) |

`text_items` is the layer underneath `.text`: instead of one flat
string, you get where each piece of text sits on the page (`x`, `y`,
`width`, `height`, in the same point units as the page itself) and what
font/size it was set in. This is the foundation later lessons build on:
form fields and annotations (Lesson 6, 9) come with their own rects in
this same coordinate space.

## The code, piece by piece

```python
for page in result.pages:
    print(page.page_num, page.width, page.height, len(page.text))
```

Straightforward iteration. Note `page.text` here is that page's own
text, not the whole document's, this document only has one page so they
happen to match, but on a multi-page PDF they wouldn't.

```python
first_item = page.text_items[0]
print(first_item.text, first_item.x, first_item.y, first_item.font_name, first_item.font_size)
```

The document's title, as a single `TextItem`, positioned near the top
of the page (`y=56.7`, close to 0 which is the page's top edge in
LiteParse's top-left-origin coordinate system) in a 10pt monospaced
font.

```python
page_one = result.get_page(1)
missing = result.get_page(99)
```

`get_page(n)` is a convenience lookup by 1-indexed page number, an
alternative to `result.pages[n - 1]`. It returns `None` instead of
raising when the page doesn't exist, worth checking for if page numbers
come from somewhere outside your control (like user input).

## Running it

```bash
uv run python lessons/liteparse/01_beginner/04_pages_and_layout/lesson.py
```

## Expected output

```
lessons/liteparse/sample_data/employee_handbook.pdf: 1 page(s)

--- page 1 ---
  size: 595 x 842 points
  text length: 1070 characters
  text items: 20
  first item: 'Northwind Trading Co. - Employee Handbook' at (x=56.8, y=56.7), font=LiberationMono, size=10.0

result.get_page(1) found page_num=1: True
result.get_page(99): None
```

## Checkpoint

- `result.pages`: a list of `ParsedPage`, one per page, in order.
- `page.text`: that page's own text, distinct from `result.text`
  (the whole document, flattened).
- `page.text_items`: the finer-grained layer, one `TextItem` per text
  run, with its own bounding box and font info.
- `result.get_page(n)`: a 1-indexed, `None`-safe page lookup.

If anything here still feels unclear, ask before moving to Lesson 5.
