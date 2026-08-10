# Lesson 2: Your first `.parse()` call

## The three things every lesson from here on reuses

Almost every lesson in this course is a variation on the same three
lines:

```python
parser = liteparse.LiteParse()
result = parser.parse("some/file.pdf")
text = result.text
```

1. **`LiteParse(...)`**: builds a parser, configured once, with whatever
   options you want (this course covers most of them). Called with no
   arguments, you get the defaults.
2. **`.parse(path)`**: runs the parse. Local, synchronous, returns a
   `ParseResult`.
3. **`.text`**: the whole document's text, all pages concatenated in
   reading order, as a single string. This is almost always what you
   want for feeding a document into search, an LLM prompt, or a keyword
   check. Lesson 4 covers `.pages` for anything that needs to stay
   per-page.

## A note on what you'll see printed

Run this lesson and you'll see a few `[liteparse] ...` timing lines
before the actual output. Those come from LiteParse itself, not this
lesson's code, they're on by default (`quiet=False` unless you set it).
You'll also notice an `ocr:` line taking most of the time, even though
`product_spec.pdf` is a completely normal, native-text PDF with no
scanned content at all.

That's `LiteParse()`'s default `ocr_enabled=True` at work: with no
argument telling it otherwise, LiteParse runs a page through OCR
whenever its internal heuristics think OCR might recover more text than
the native text layer alone, and one of those heuristics ("sparse-text")
can trigger even on a page that already has plenty of real text, if the
text happens to cover a small fraction of the page's visual area. The
OCR pass ran here, but it didn't change `result.text`, since the native
text layer already had everything. Lesson 8 covers this heuristic and
the OCR contrast properly; Lesson 3 shows how to turn it off with
`ocr_enabled=False` when you already know your documents are
native-text.

## Running it

```bash
uv run python lessons/liteparse/01_beginner/02_first_parse_call/lesson.py
```

## Expected output

```
[liteparse] extract: 1.1ms (1 pages)
[liteparse] ocr render: 6.1ms (1 pages)
[liteparse] ocr: 846.8ms
[liteparse] project: 0.2ms
[liteparse] total: 854.2ms

Parsed: lessons/liteparse/sample_data/product_spec.pdf
Character count: 677

--- result.text ---
Product Specification: Aurora Desk Lamp Mk II

Model: AUR-DL-200
Category: Home Office Lighting
Status: In Production

Key Specifications:
Power Source: USB-C, 5V/2A
Brightness Levels: 5, from 200 to 1200 lumens
Color Temperature: 2700K to 6500K, adjustable
Weight: 680 grams
Base Diameter: 15 centimeters
Arm Reach: 45 centimeters extended
Warranty: 2 years, parts and labor
Certifications: CE, FCC, RoHS

Description:

The Aurora Desk Lamp Mk II is a fully adjustable LED desk lamp
designed for long reading and work sessions. Its aluminum arm holds
position at any angle, and the touch-sensitive base remembers the
last brightness and color temperature setting between uses.
```

The exact millisecond values will vary between runs and machines; the
text itself will not.

## Checkpoint

- **`LiteParse()`**: builds a parser; every configuration option has a
  default, so this works with zero arguments.
- **`.parse(path)`**: local, synchronous, returns a `ParseResult`.
- **`.text`**: the whole document's text as one string, the field
  you'll reach for most often.
- **`ocr_enabled` defaults to `True`**: LiteParse can run OCR on a page
  even when native text exists, based on internal heuristics, not just
  when a page is obviously scanned. More on this in Lessons 3 and 8.

If anything here still feels unclear, ask before moving to Lesson 3.
