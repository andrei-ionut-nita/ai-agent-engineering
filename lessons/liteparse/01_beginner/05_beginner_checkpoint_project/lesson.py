"""
Lesson 5 (Checkpoint): batch-parse the sample_data PDFs to .txt files with
a per-file summary.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/liteparse/01_beginner/05_beginner_checkpoint_project/lesson.py

This combines everything from the beginner tier: LiteParse() with
ocr_enabled=False (Lesson 3), .parse() and .text (Lesson 2), and
result.num_pages (Lesson 4), applied to every PDF in sample_data/ in one
pass. It also writes one .txt file per PDF, a genuinely common first
step in a document pipeline: turn a folder of PDFs into a folder of
plain text before anything else happens to it.
"""

import tempfile
from pathlib import Path

import liteparse

SAMPLE_DATA_DIR = Path("lessons/liteparse/sample_data")


def main() -> None:
    # Glob every top-level PDF in sample_data/, skipping the _src/
    # subfolder (that holds the raw .txt/.png sources the PDFs were
    # built from, not something this lesson should try to parse).
    pdf_paths = sorted(SAMPLE_DATA_DIR.glob("*.pdf"))

    # One parser, reused for every file (Lesson 3's point about
    # configuring once). ocr_enabled=False because this batch includes
    # scanned_notice.pdf, a genuinely image-only scan with no text
    # layer at all: with OCR off, LiteParse can't recover its text, and
    # that's the point of this lesson, a batch that quietly includes
    # one document your pipeline can't actually read yet. Lesson 8
    # turns OCR back on and shows what changes.
    parser = liteparse.LiteParse(ocr_enabled=False, quiet=True)

    output_dir = Path(tempfile.mkdtemp(prefix="liteparse_lesson05_"))
    print(f"Writing .txt output to: {output_dir}\n")

    print(f"{'file':<24} {'pages':>6} {'chars':>8}  txt_output")
    print("-" * 70)

    total_chars = 0
    for pdf_path in pdf_paths:
        result = parser.parse(pdf_path)

        txt_path = output_dir / f"{pdf_path.stem}.txt"
        txt_path.write_text(result.text, encoding="utf-8")

        total_chars += len(result.text)
        print(f"{pdf_path.name:<24} {result.num_pages:>6} {len(result.text):>8}  {txt_path.name}")

    print("-" * 70)
    print(f"{len(pdf_paths)} file(s) parsed, {total_chars} total characters written")

    print(
        "\nNote: scanned_notice.pdf shows 0 characters here, it's a genuinely "
        "scanned page with no text layer, and ocr_enabled=False means "
        "LiteParse never tries to recover its text via OCR. Lesson 8 covers "
        "exactly this contrast."
    )


if __name__ == "__main__":
    main()
