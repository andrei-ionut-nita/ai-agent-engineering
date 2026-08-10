"""Lesson 17: comparing docling, markitdown, and liteparse.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/03_advanced/17_comparing_docling_markitdown_liteparse/lesson.py

Requires markitdown and liteparse to be installed, both are already
project dependencies (see lessons/markitdown/ and lessons/liteparse/).
"""

import time
from pathlib import Path

import liteparse
from docling.document_converter import DocumentConverter
from markitdown import MarkItDown

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"
PDF_PATH = SAMPLE_DATA / "quarterly_report.pdf"


def main() -> None:
    print(f"Comparing conversions of: {PDF_PATH.name}\n")

    md = MarkItDown()
    start = time.perf_counter()
    md_result = md.convert(PDF_PATH)
    md_seconds = time.perf_counter() - start
    print("=== markitdown ===")
    print(md_result.markdown[:350])
    print(f"(markitdown: {len(md_result.markdown)} chars, {md_seconds:.3f}s)\n")

    lp = liteparse.LiteParse()
    start = time.perf_counter()
    lp_result = lp.parse(PDF_PATH)
    lp_seconds = time.perf_counter() - start
    print("=== liteparse ===")
    print(lp_result.text[:350])
    print(f"(liteparse: {len(lp_result.text)} chars, {lp_seconds:.3f}s)\n")

    converter = DocumentConverter()
    start = time.perf_counter()
    docling_result = converter.convert(PDF_PATH)
    docling_seconds = time.perf_counter() - start
    docling_markdown = docling_result.document.export_to_markdown()
    print("=== docling ===")
    print(docling_markdown[:350])
    print(
        f"(docling: {len(docling_markdown)} chars, {docling_seconds:.3f}s, "
        f"tables detected: {len(docling_result.document.tables)})\n"
    )

    # The interesting comparison isn't total character count, it's
    # whether the table survived as a real table. markitdown and
    # liteparse both read the PDF's raw text stream in column order,
    # with no model deciding where one table column ends and the next
    # begins, so adjacent columns can merge into one. docling's
    # TableFormer explicitly reconciles the table grid into a known
    # number of rows and columns.
    print("=== Observations ===")
    print(f"markitdown header row: {_header_line(md_result.markdown)!r}")
    print(f"liteparse header row:  {_header_line(lp_result.text)!r}")
    print(
        f"docling table shape:   {docling_result.document.tables[0].data.num_rows} rows x "
        f"{docling_result.document.tables[0].data.num_cols} columns (Region and "
        "Product Line kept as separate columns)"
    )


def _header_line(text: str) -> str:
    for line in text.splitlines():
        if "Region" in line and "Growth" in line:
            return line.strip()
    return "(not found)"


if __name__ == "__main__":
    main()
