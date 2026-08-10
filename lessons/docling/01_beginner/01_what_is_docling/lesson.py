"""Lesson 1: what docling is, and why it exists.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/01_beginner/01_what_is_docling/lesson.py
"""

from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter


def main() -> None:
    # No arguments needed. DocumentConverter's default constructor
    # already knows how to route every supported InputFormat to the
    # right backend and pipeline, that's the whole point of a single
    # entry point library.
    converter = DocumentConverter()

    # allowed_formats isn't set here, so this reflects every format the
    # installed docling build supports, not a hand-picked subset.
    supported = sorted(fmt.value for fmt in InputFormat)

    print(f"docling supports {len(supported)} input formats:")
    for fmt in supported:
        print(f"  - {fmt}")

    print()
    print("This course focuses mainly on: pdf, docx, pptx.")
    print(f"DocumentConverter instance ready: {converter!r}")


if __name__ == "__main__":
    main()
