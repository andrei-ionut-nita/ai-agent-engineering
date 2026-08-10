# Lesson 11 (Checkpoint): Auto-detecting OCR need

## The gap this closes

Lesson 5's checkpoint parsed every file with OCR off, fast, but wrong
for `scanned_notice.pdf`. Lesson 8 turned OCR on and got that file's
text back, but at the cost of an OCR pass on every page, including
the four that never needed it. Neither extreme is right for a real
mixed batch. This checkpoint tries the cheap path first and only pays
for OCR on the files that actually need it.

## The strategy: try fast, fall back on near-zero yield

```python
result = parser_no_ocr.parse(pdf_path)
if len(result.text.strip()) < NEAR_ZERO_TEXT_CHARS:
    result = parser_ocr.parse(pdf_path)
```

Parse with `ocr_enabled=False` first. If the text that comes back is
near-empty (under a small character threshold), the document almost
certainly has no usable native text layer, so re-parse it with
`ocr_enabled=True` to recover text via OCR. This is deliberately blunt
(a genuinely tiny native-text page could, in principle, trip it), but
it's fast, simple, and gets every file in this batch right.

## Why `is_complex().needs_ocr` alone is not enough here

Lesson 8 introduced `is_complex()` as a cheap way to see LiteParse's own
OCR decision without a full parse. Run it against this whole batch and
`needs_ocr` comes back `True` for **every single file**, including the
three plain, perfectly native-text documents whose OCR-off parse
already recovered complete, correct text. The reason is the
`sparse-text` heuristic: these are short, mostly-whitespace pages (a
one-page memo, a one-page form), so native text covers only 2-14% of
the page area, low enough to trip a heuristic tuned to catch pages
where whatever native text exists might be an artifact rather than the
whole story. The heuristic isn't wrong to be cautious, but it's not a
reliable "does this file need OCR" verdict for a batch like this one.

The text-yield fallback in this lesson doesn't have that problem: it
checks what the fast parse **actually returned**, not a layout
proportion, so it correctly leaves the three native-text files alone
and only re-parses `scanned_notice.pdf` with OCR. The practical
takeaway: use `is_complex()` as a cheap pre-parse triage signal when
you want it (e.g. to sort a huge batch before committing CPU time), but
for a correctness-critical fallback decision, checking the real output
of a fast parse is more reliable than trusting a heuristic verdict
blindly.

## Running it

```bash
uv run python lessons/liteparse/02_intermediate/11_intermediate_checkpoint_project/lesson.py
```

## Expected output

```
file                        chars  used_ocr   is_complex.needs_ocr
----------------------------------------------------------------------
employee_handbook.pdf        1070     False                   True
intake_form.pdf               158     False                   True
product_spec.pdf              677     False                   True
scanned_notice.pdf            183      True                   True
vendor_memo.pdf               242     False                   True
----------------------------------------------------------------------
Unified 5 document(s), 2330 total characters, into one in-memory batch

Note the mismatch: is_complex().needs_ocr fires True for EVERY file here, including the three native-text documents whose fast, OCR-off parse already recovered real text. That's the 'sparse-text' heuristic: these are short, mostly-whitespace pages (a one-page memo, a form), so native text covers only 2-14% of the page area, enough to trip the heuristic even though the text itself is complete and correct. The text-yield fallback in this lesson isn't fooled, because it checks what the fast parse actually returned, not a layout signal. Treat is_complex() as a cheap PRE-parse triage hint, not a final verdict, for a batch job like this one.
```

## Checkpoint

- A "try fast, fall back on near-zero yield" strategy correctly handles
  a mixed native + scanned batch while only paying OCR cost where it's
  actually needed.
- `is_complex().needs_ocr` is a heuristic, not a guarantee, it can flag
  perfectly good native-text pages (short/sparse layouts especially).
- Checking a fast parse's actual text yield is a more reliable
  fallback trigger than trusting a pre-parse heuristic alone.

This closes out the intermediate tier. If anything from Lessons 6-11
still feels unclear, ask before moving to Lesson 12 and the advanced
tier.
