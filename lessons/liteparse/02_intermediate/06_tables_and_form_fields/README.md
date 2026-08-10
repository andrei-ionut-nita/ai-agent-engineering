# Lesson 6: Form fields

## A quick note on "tables"

LiteParse doesn't have a dedicated `extract_tables()` method the way
some parsers do. Tables surface two other ways instead: as `Table`
elements in a tagged PDF's structure tree (Lesson 10, and only present
if the PDF was authored with accessibility tags), and as layout signals
(`ruled_table_count`, `text_table_run_count`) in the per-page complexity
stats (Lesson 8/11). None of this course's sample PDFs happen to
contain a real table, so this lesson focuses on what `intake_form.pdf`
actually has: real AcroForm fields, a genuinely common and more
reliably structured case than table detection.

## AcroForm fields are widgets, not text

`intake_form.pdf` was built as an actual fillable PDF form: text boxes,
a radio button group, and a checkbox, each a distinct widget object in
the PDF, not just text laid out to look form-like. `extract_form_fields=True`
walks those widgets and returns them as structured `FormField` objects
instead of leaving them as unstructured text on the page.

## `FormField`, field by field

| Field | Meaning |
|---|---|
| `name` / `id` | The field's internal name (what a form-filling tool would target) |
| `type` | `"text"`, `"radio"`, `"checkbox"`, etc. |
| `alternate_name` | The human-readable label (`/TU` in the PDF spec) |
| `value` | The field's current value, `None` if unset |
| `checked` | For radio/checkbox widgets: whether this specific widget is selected |
| `export_value` | The value submitted if this option is selected |
| `control_index` / `control_count` | Which button this is within a radio group, and how many buttons the group has |

A radio button group is worth pausing on: `contact_method` appears
**twice** in the output below, once per button ("Email" and "Phone"),
because each button in a PDF radio group is its own widget/annotation.
They share the same `name`, and `control_index` (0, 1, ...) tells you
which button within the group each `FormField` represents.

## The code, piece by piece

```python
parser = liteparse.LiteParse(ocr_enabled=False, quiet=True, extract_form_fields=True)
```

`extract_form_fields=True` is off by default (most PDFs have no
AcroForm fields at all), so it costs nothing on documents that don't
need it.

```python
page = result.pages[0]
for field in page.form_fields:
    ...
```

Form fields live on `page.form_fields`, a page-scoped list, since
widgets are placed on specific pages. It's `None` unless
`extract_form_fields=True` was set, distinct from `text_items`, which
is always populated.

## Running it

```bash
uv run python lessons/liteparse/02_intermediate/06_tables_and_form_fields/lesson.py
```

## Expected output

```
lessons/liteparse/sample_data/intake_form.pdf: 5 form field(s) found

  field: 'full_name' (id='full_name')
    type: text, label: 'Full name'
    value: None

  field: 'email' (id='email')
    type: text, label: 'Email address'
    value: None

  field: 'contact_method' (id='contact_method')
    type: radio, label: 'Email'
    option 0: checked=True, export_value='email'

  field: 'contact_method' (id='contact_method')
    type: radio, label: 'Email'
    option 1: checked=False, export_value=None

  field: 'newsletter' (id='newsletter')
    type: checkbox, label: 'Subscribe'
    checked: True, export_value='Yes'
```

## Checkpoint

- LiteParse extracts real form widgets via `extract_form_fields=True`,
  not a generic "tables" feature; table detection lives elsewhere
  (structure tree tags, complexity signals).
- `FormField.type` distinguishes text/radio/checkbox widgets, each with
  slightly different meaningful fields (`value` vs `checked`/`export_value`).
- A radio group produces one `FormField` per button, sharing a `name`,
  distinguished by `control_index`.

If anything here still feels unclear, ask before moving to Lesson 7.
