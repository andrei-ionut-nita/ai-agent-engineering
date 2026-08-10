"""Lesson 15: batch conversion and reusing one converter.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/03_advanced/15_batch_conversion_and_performance/lesson.py
"""

import time
from pathlib import Path

from docling.document_converter import DocumentConverter

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"

FILES = [
    "quarterly_report.pdf",
    "project_plan.docx",
    "team_update.pptx",
    "research_note.pdf",
]


def main() -> None:
    # Every earlier lesson constructed a fresh DocumentConverter per
    # script, that's fine for a single conversion, but constructing one
    # is not free: model weights get loaded into memory the first time
    # each is used. A real batch job builds one DocumentConverter and
    # reuses it across every file, exactly what convert_all() does.
    converter = DocumentConverter()

    start = time.perf_counter()
    results = list(converter.convert_all([SAMPLE_DATA / f for f in FILES]))
    elapsed = time.perf_counter() - start

    print(f"Converted {len(results)} files with one reused converter in {elapsed:.2f}s\n")
    for result in results:
        name = result.input.file.name
        status = result.status
        print(f"  {name:<24} {status}  texts={len(result.document.texts)}")

    print()
    print(
        "Compare this to constructing a new DocumentConverter() per file: "
        "each one would re-check model availability and re-initialize "
        "pipelines, even though the same underlying weights end up loaded "
        "either way. One converter, many files, is the right shape for a "
        "batch job."
    )


if __name__ == "__main__":
    main()
