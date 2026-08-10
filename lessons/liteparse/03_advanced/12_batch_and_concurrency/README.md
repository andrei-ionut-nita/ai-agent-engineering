# Lesson 12: Batch parsing and concurrency

## Two different kinds of concurrency

This lesson deliberately separates two things that are easy to conflate:

1. **Parallelizing across files**: parsing several separate documents
   at the same time, your own code's job (this lesson uses
   `concurrent.futures.ThreadPoolExecutor`).
2. **`num_workers`**: LiteParse's own internal knob for how many OCR
   jobs run concurrently *inside a single `.parse()` call*, when one
   multi-page document has several pages that all need OCR.

They solve different problems and don't substitute for each other.

## Why threads, for a Rust extension

Python's GIL normally means threads don't help CPU-bound work. LiteParse's
actual parsing and OCR work happens in its Rust extension module, and
that native code releases the GIL while it runs, the same reason
libraries like NumPy get real speedup from threads for their heavy
lifting. That's why `ThreadPoolExecutor` (not `multiprocessing`, with
its heavier process-startup and serialization cost) is a reasonable
choice for parallelizing a LiteParse batch.

## The code, piece by piece

```python
pdf_paths = sorted(SAMPLE_DATA_DIR.glob("*.pdf")) * REPEAT_COUNT
parser = liteparse.LiteParse(quiet=True)
```

The batch repeats this course's 5 sample files 3 times (15 total) and
leaves `ocr_enabled` at its default. That's intentional: the batch
includes `scanned_notice.pdf`, whose OCR pass is genuinely slow
(hundreds of milliseconds, Lesson 8), the kind of work concurrency
actually helps with. A pure native-text batch parses so fast per file
that thread-pool overhead would swamp the real timing signal.

```python
for pdf_path in pdf_paths:
    parser.parse(pdf_path)
```

Sequential baseline: one file at a time.

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    list(executor.map(parser.parse, pdf_paths))
```

The same parser instance, reused across threads (safe, each `.parse()`
call is independent and doesn't mutate shared state), spread across 4
worker threads.

```python
config = liteparse.LiteParse(num_workers=2).get_config()
```

`num_workers` (default: CPU cores - 1) caps how many OCR tasks run in
parallel when a *single* multi-page document needs OCR on several
pages at once. `get_config()` returns the parser's resolved
`LiteParseConfig`, confirming the value actually took. It has no
visible effect on this lesson's single-page sample PDFs and does
nothing for parallelizing across separate files, that's this lesson's
`ThreadPoolExecutor`, not a LiteParse feature.

## Running it

```bash
uv run python lessons/liteparse/03_advanced/12_batch_and_concurrency/lesson.py
```

## Expected output

```
Sequential: 15 files in 9.19s
Threaded (4 workers): 15 files in 3.38s
Speedup: 2.7x

num_workers=2 configured: 2
num_workers governs OCR concurrency WITHIN a single multi-page document's .parse() call, not across separate files in a batch like this lesson's ThreadPoolExecutor does.
```

Exact timings and the speedup ratio depend heavily on your machine's
CPU core count; the direction (threaded meaningfully faster) should
hold on any multi-core machine.

## Checkpoint

- Parallelizing across files is your own code's responsibility
  (`ThreadPoolExecutor` works because LiteParse's native code releases
  the GIL).
- `num_workers` is a separate, narrower knob: OCR concurrency inside
  one document's multi-page parse, not a batch-level setting.
- OCR-heavy batches benefit the most from concurrency; fast native-text
  batches may not show much difference at all.

If anything here still feels unclear, ask before moving to Lesson 13.
