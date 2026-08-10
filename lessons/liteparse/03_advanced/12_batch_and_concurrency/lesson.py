"""
Lesson 12: num_workers and timing a concurrent batch parse.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/liteparse/03_advanced/12_batch_and_concurrency/lesson.py

This lesson times the same batch of files parsed two ways: one file at
a time, in a loop, versus spread across threads with
concurrent.futures.ThreadPoolExecutor. It also explains num_workers,
LiteParse's own internal concurrency knob, which governs something
different: how many OCR jobs run in parallel WITHIN a single .parse()
call, not across files.
"""

import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import liteparse

SAMPLE_DATA_DIR = Path("lessons/liteparse/sample_data")

# Repeat the 5 sample files a few times so the batch is big enough for
# the timing difference to be visible and not just noise.
REPEAT_COUNT = 3


def main() -> None:
    pdf_paths = sorted(SAMPLE_DATA_DIR.glob("*.pdf")) * REPEAT_COUNT

    # ocr_enabled left at its default (True) on purpose: this batch
    # includes scanned_notice.pdf several times, and OCR is exactly the
    # slow, CPU-bound work concurrency actually helps with. A pure
    # native-text batch parses so fast (single-digit milliseconds per
    # file, Lesson 1) that thread overhead would dominate the timing
    # instead of the work itself.
    parser = liteparse.LiteParse(quiet=True)

    # Sequential: one file at a time, in a plain loop.
    start = time.perf_counter()
    for pdf_path in pdf_paths:
        parser.parse(pdf_path)
    sequential_seconds = time.perf_counter() - start
    print(f"Sequential: {len(pdf_paths)} files in {sequential_seconds:.2f}s")

    # Threaded: the SAME parser instance, reused across threads (it's
    # safe to share, each .parse() call is independent), spread across
    # a thread pool. This parallelizes ACROSS files/documents, using
    # Python's own concurrency, since each .parse() call releases the
    # GIL while doing the actual (Rust-side) parsing/OCR work.
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(parser.parse, pdf_paths))
    threaded_seconds = time.perf_counter() - start
    print(f"Threaded (4 workers): {len(pdf_paths)} files in {threaded_seconds:.2f}s")

    speedup = sequential_seconds / threaded_seconds if threaded_seconds else 0
    print(f"Speedup: {speedup:.1f}x")

    # num_workers is a DIFFERENT knob: it caps how many OCR tasks run
    # concurrently INSIDE one .parse() call, when that single document
    # has multiple pages that all need OCR (default: CPU cores - 1).
    # It has no effect on this lesson's single-page sample PDFs, and it
    # doesn't parallelize across separate files the way the
    # ThreadPoolExecutor above does, that's a batch-level concern this
    # lesson's own code handles, not something LiteParse manages for you.
    config = liteparse.LiteParse(num_workers=2).get_config()
    print(f"\nnum_workers=2 configured: {config.num_workers}")
    print(
        "num_workers governs OCR concurrency WITHIN a single multi-page "
        "document's .parse() call, not across separate files in a batch "
        "like this lesson's ThreadPoolExecutor does."
    )


if __name__ == "__main__":
    main()
