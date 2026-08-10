# Lesson 3: Parser configuration options

## `LiteParse()` is where you configure, not `.parse()`

Every option in this lesson (and almost every option in this course) is
a keyword argument to `LiteParse(...)`, not to `.parse(path)`. You build
one configured parser, then call `.parse()` on as many files as you
want with that same configuration. This matters for later lessons on
batching: build the parser once, reuse it.

## The options this lesson covers

| Option | What it does |
|---|---|
| `ocr_enabled` | `True` by default; `False` skips OCR entirely, faster and quieter when you know your documents are native-text |
| `max_pages` | Caps how many pages get parsed, from the start of the document |
| `target_pages` | Parses specific pages by number/range, e.g. `"1-5,10,15-20"` |
| `output_format` | `"text"` (default) or `"markdown"`, the latter also populates `result.pages[i].markdown` |
| `password` | Unlocks an encrypted PDF; harmless to pass on a document that doesn't need it |

## The code, piece by piece

```python
fast_parser = liteparse.LiteParse(ocr_enabled=False, quiet=True)
```

Turns off the OCR heuristics Lesson 2 ran into. On a document you know
is native-text, this is both faster (no OCR render/inference pass) and
quieter (no `[liteparse] ocr: ...` timing logs).

```python
capped = liteparse.LiteParse(ocr_enabled=False, quiet=True, max_pages=1)
targeted = liteparse.LiteParse(ocr_enabled=False, quiet=True, target_pages="1")
```

`max_pages=1` stops after the first page, useful for previewing a large
document cheaply. `target_pages="1"` instead names specific pages; on a
1-page sample PDF both produce the same 1-page result, but on a longer
document they diverge: `max_pages=3` always gets pages 1-3, while
`target_pages="4-6"` gets exactly pages 4 through 6.

```python
markdown_parser = liteparse.LiteParse(ocr_enabled=False, quiet=True, output_format="markdown")
```

With `output_format="markdown"`, each `ParsedPage` gets a populated
`.markdown` field alongside `.text`. Note the actual output below: on
`product_spec.pdf`, LiteParse wrapped the whole page in a ` ```python `
fence. That's LiteParse's Markdown renderer applying a code-block
heuristic to text it judged monospaced/structured-looking (a spec sheet
with a lot of `Key: Value` lines can trigger this); it's not a bug in
this lesson, just a real quirk worth knowing about before you rely on
Markdown output for downstream rendering.

```python
unlock_attempt = liteparse.LiteParse(ocr_enabled=False, quiet=True, password="not-actually-needed")
```

None of this course's sample PDFs are password-protected, so this call
behaves identically to not passing `password` at all. On an actual
encrypted PDF, the right password lets parsing proceed normally; the
wrong one (or none) raises `liteparse.ParseError`.

## Running it

```bash
uv run python lessons/liteparse/01_beginner/03_parse_config_options/lesson.py
```

## Expected output

```
ocr_enabled=False: 1070 chars, 1 page(s)
max_pages=1: 1 page(s) returned
target_pages='1': 1 page(s) returned

output_format='markdown', first 200 chars of result.pages[0].markdown:
```python
Product Specification: Aurora Desk Lamp Mk II
Model: AUR-DL-200
Category: Home Office Lighting
Status: In Production
Key Specifications:
Power Source: USB-C, 5V/2A
Brightness Levels: 5, from

password=<ignored on an unencrypted PDF>: 1070 chars, no error
```

## Checkpoint

- Configuration lives on `LiteParse(...)`, reused across every
  `.parse()` call you make with that instance.
- `ocr_enabled=False` is the right default for a batch you already know
  is native-text.
- `max_pages` truncates from the start; `target_pages` selects specific
  pages/ranges.
- `output_format="markdown"` can misfire its code-fence heuristic on
  structured but non-code text, don't assume it's always clean.
- `password` is safe to pass even when it isn't needed.

If anything here still feels unclear, ask before moving to Lesson 4.
