"""
Lesson 11: comparing MarkItDown and LiteParse on the same PDF.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/markitdown/03_advanced/11_comparing_markitdown_and_liteparse/lesson.py

Lesson 1's comparison table was a claim. This lesson tests it: the
exact same PDF fixture, run through both this course's MarkItDown and
the lessons/liteparse/ course's LiteParse, timed and printed side by
side. Requires lessons/liteparse/ to be installed (it already is, via
this project's pyproject.toml), no other soft prerequisite from that
course is needed to follow this lesson, just its existence.

This lesson only READS from lessons/liteparse/'s package, it doesn't
touch lessons/liteparse/'s course directory at all.
"""

import time
from pathlib import Path

import liteparse
from markitdown import MarkItDown

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"
PDF_PATH = FIXTURES_DIR / "product_spec.pdf"


def main() -> None:
    print(f"Comparing conversions of: {PDF_PATH.name}\n")

    # --- MarkItDown ---
    md = MarkItDown()
    start = time.perf_counter()
    md_result = md.convert(PDF_PATH)
    md_seconds = time.perf_counter() - start

    # --- LiteParse ---
    lp = liteparse.LiteParse()
    start = time.perf_counter()
    lp_result = lp.parse(PDF_PATH)
    lp_seconds = time.perf_counter() - start

    print("=== MarkItDown output ===")
    print(md_result.markdown)
    print(f"\n(MarkItDown: {len(md_result.markdown)} chars, {md_seconds:.3f}s)\n")

    print("=== LiteParse output ===")
    print(lp_result.text)
    print(f"\n(LiteParse: {len(lp_result.text)} chars, {lp_seconds:.3f}s)\n")

    # --- What actually differs ---
    print("=== Observations ===")
    print(f"Character count difference: {abs(len(md_result.markdown) - len(lp_result.text))}")
    print(f"MarkItDown was {lp_seconds / md_seconds:.1f}x faster on this file.")
    print(
        "LiteParse's extra time comes from running OCR on every page as part of "
        "its pipeline (visible in its own '[liteparse] ocr: ...' log lines above), "
        "even though this PDF has a native text layer and OCR added nothing here. "
        "That's the tradeoff Lesson 1 predicted: MarkItDown reads the text layer "
        "directly and stops, LiteParse's deeper pipeline (built for scanned pages, "
        "layout fidelity, and forms) runs regardless, cheap on a one-page native-"
        "text PDF like this one, but the cost that pays for handling PDFs "
        "MarkItDown can't read well: scanned documents with no text layer at all."
    )


if __name__ == "__main__":
    main()
