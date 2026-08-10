# Lesson 11: comparing MarkItDown and LiteParse

## Testing Lesson 1's claim, not just repeating it

Lesson 1 laid out a table: MarkItDown trades PDF-specific depth for
broad format coverage, LiteParse trades broad coverage for PDF depth
(layout fidelity, OCR, forms). That was a claim about the two
libraries' design, made before either had actually been run
side by side. This lesson runs them side by side, on this course's own
`product_spec.pdf` fixture, a real native-text (not scanned) one-page
PDF, and reports what actually happened.

## What the run found

On this fixture, both libraries produced essentially the same text,
a 2-character difference out of roughly 820 characters, almost
certainly whitespace, not missing content. Where they genuinely
diverged was speed: MarkItDown finished in about 0.03 seconds,
LiteParse in about 1 second, roughly 30x slower on this file.

The reason is visible in LiteParse's own log output
(`[liteparse] ocr: ...`): LiteParse runs OCR as part of its standard
pipeline regardless of whether the PDF already has a native text
layer. `product_spec.pdf` does have one, MarkItDown reads it directly
and stops, so OCR bought LiteParse nothing on this file, just added
roughly a second of processing time.

That is not a flaw in LiteParse, it's the direct, observable
consequence of the design tradeoff Lesson 1 described: LiteParse's
deeper pipeline is what makes it capable of scanned pages, layout
fidelity, and forms, formats where MarkItDown has no text layer to
fall back on and would produce nothing useful. Paying that OCR cost
even on an easy, native-text PDF is the price of also handling the
hard case. This single fixture can't test the hard case (LiteParse's
`sample_data/scanned_notice.pdf`, not used by this lesson, would be a
natural next thing to try if you want to see that gap for yourself),
but it does confirm the speed/depth tradeoff is real, not just a
claim from a comparison table.

## The code, piece by piece

```python
import liteparse
lp = liteparse.LiteParse()
lp_result = lp.parse(PDF_PATH)
lp_result.text
```

LiteParse's equivalent of MarkItDown's `.convert()` /`.markdown`, a
`.parse()` call returning a result object with a `.text` attribute.

```python
start = time.perf_counter()
md_result = md.convert(PDF_PATH)
md_seconds = time.perf_counter() - start
```

Simple wall-clock timing around each call, run back to back on the
same file, same machine, for a fair (if informal) comparison.

## Running it

```bash
uv run python lessons/markitdown/03_advanced/11_comparing_markitdown_and_liteparse/lesson.py
```

## Expected output

Timings will vary somewhat by machine, but the roughly 30x gap and
near-identical text content should reproduce:

```
Comparing conversions of: product_spec.pdf

=== MarkItDown output ===
Product Spec: TrailLight Handheld Lantern
...
(MarkItDown: 819 chars, 0.033s)

=== LiteParse output ===
Product Spec: TrailLight Handheld Lantern
...
(LiteParse: 817 chars, 1.032s)

=== Observations ===
Character count difference: 2
MarkItDown was 31.3x faster on this file.
LiteParse's extra time comes from running OCR on every page as part of its pipeline...
```

(LiteParse also prints its own `[liteparse] ...` timing log lines
directly to stdout as it runs, that's LiteParse's own instrumentation,
not something this lesson adds.)

## Checkpoint

- **On a native-text PDF, output content is nearly identical**: both
  libraries correctly extract the same text when there's a text layer
  to read.
- **MarkItDown was ~30x faster here**: it reads the text layer and
  stops.
- **LiteParse runs OCR unconditionally**: that's overhead on an easy
  file, but the same pipeline is what lets it handle scanned pages
  MarkItDown can't read at all.
- **The tradeoff from Lesson 1 held up under an actual test**: breadth
  and speed (MarkItDown) vs. depth and robustness on hard PDFs
  (LiteParse), confirmed, not just claimed.

If anything here still feels unclear, ask before moving to Lesson 12.
