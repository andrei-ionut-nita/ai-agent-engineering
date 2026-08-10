"""
Lesson 11 (Checkpoint): auto-detecting which PDFs need OCR, and unifying
a mixed native + scanned batch into one output.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/liteparse/02_intermediate/11_intermediate_checkpoint_project/lesson.py

Lesson 5 batch-parsed sample_data/ with OCR off and got one file back
empty. Lesson 8 showed turning OCR on fixes that file, but at the cost
of a slow OCR pass on every page, including ones that never needed it.
This checkpoint builds the missing piece: try the fast path first, and
only fall back to the slow OCR path for files that actually need it.
"""

from pathlib import Path

import liteparse

SAMPLE_DATA_DIR = Path("lessons/liteparse/sample_data")

# A cheap, deliberately blunt threshold: if the fast, OCR-off parse
# yields fewer characters than this, treat the document as needing OCR.
# It's not perfect (a genuinely short but native-text page could trip
# it), but it's simple, fast, and correct for every document in this
# course's sample_data/.
NEAR_ZERO_TEXT_CHARS = 20


def parse_with_ocr_fallback(parser_no_ocr: liteparse.LiteParse, parser_ocr: liteparse.LiteParse, pdf_path: Path):
    # Fast path first: try native-text-only parsing, which is cheap
    # (single-digit milliseconds, Lesson 1) and correct for the common
    # case of a native-text PDF.
    result = parser_no_ocr.parse(pdf_path)
    used_ocr = False

    if len(result.text.strip()) < NEAR_ZERO_TEXT_CHARS:
        # Near-zero yield: this document likely has no usable native
        # text layer at all (a scan), so fall back to the slower,
        # OCR-enabled parser to actually recover its text.
        result = parser_ocr.parse(pdf_path)
        used_ocr = True

    return result, used_ocr


def main() -> None:
    pdf_paths = sorted(SAMPLE_DATA_DIR.glob("*.pdf"))

    parser_no_ocr = liteparse.LiteParse(ocr_enabled=False, quiet=True)
    parser_ocr = liteparse.LiteParse(ocr_enabled=True, quiet=True)

    print(f"{'file':<24} {'chars':>8}  {'used_ocr':>8}  {'is_complex.needs_ocr':>21}")
    print("-" * 70)

    unified_text_by_file: dict[str, str] = {}
    for pdf_path in pdf_paths:
        result, used_ocr = parse_with_ocr_fallback(parser_no_ocr, parser_ocr, pdf_path)
        unified_text_by_file[pdf_path.name] = result.text

        # For comparison: is_complex() (Lesson 8) gives a needs_ocr
        # verdict from LiteParse's own internal heuristics, without the
        # text-yield trick this lesson uses. Printing both side by side
        # shows they don't always agree.
        complexity = parser_ocr.is_complex(pdf_path)[0]

        print(f"{pdf_path.name:<24} {len(result.text):>8}  {str(used_ocr):>8}  {str(complexity.needs_ocr):>21}")

    print("-" * 70)
    total_chars = sum(len(t) for t in unified_text_by_file.values())
    print(f"Unified {len(unified_text_by_file)} document(s), {total_chars} total characters, into one in-memory batch")

    print(
        "\nNote the mismatch: is_complex().needs_ocr fires True for EVERY file "
        "here, including the three native-text documents whose fast, OCR-off "
        "parse already recovered real text. That's the 'sparse-text' heuristic: "
        "these are short, mostly-whitespace pages (a one-page memo, a form), "
        "so native text covers only 2-14% of the page area, enough to trip "
        "the heuristic even though the text itself is complete and correct. "
        "The text-yield fallback in this lesson isn't fooled, because it "
        "checks what the fast parse actually returned, not a layout signal. "
        "Treat is_complex() as a cheap PRE-parse triage hint, not a final "
        "verdict, for a batch job like this one."
    )


if __name__ == "__main__":
    main()
