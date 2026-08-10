"""Lesson 2: the first real .convert() call.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/01_beginner/02_first_convert_call/lesson.py
"""

from pathlib import Path

from docling.document_converter import DocumentConverter

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"


def main() -> None:
    converter = DocumentConverter()

    # convert() takes a path (str or Path), a URL, or a DocumentStream
    # (Lesson 4 in the intermediate tier touches streams). It returns a
    # ConversionResult, not the document itself, result.document is
    # the DoclingDocument.
    result = converter.convert(SAMPLE_DATA / "quarterly_report.pdf")

    print(f"Conversion status: {result.status}")
    print(f"Input format detected: {result.input.format}")
    print(f"Page count: {len(result.pages)}")

    # export_to_markdown() is the method you'll use most in this
    # course: it walks the DoclingDocument's structure and serializes
    # it as Markdown, headings become #, tables become pipe tables.
    markdown = result.document.export_to_markdown()
    print()
    print("First 500 characters of the converted Markdown:")
    print(markdown[:500])


if __name__ == "__main__":
    main()
