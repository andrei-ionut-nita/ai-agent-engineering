"""
Lesson 1: what is MarkItDown, and is it actually installed and working.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/markitdown/01_beginner/01_what_is_markitdown/lesson.py

MarkItDown converts many file formats (docx, pptx, xlsx, pdf, images,
html, and more) into Markdown, so an LLM can actually read them. This
lesson doesn't convert anything yet, that's Lesson 2, it just confirms
the library and its heavier format extras (installed here via the
`markitdown[all]` extra) are present and importable.
"""

import importlib.metadata

MARKITDOWN_VS_LITEPARSE = {
    "Format coverage": "Broad (docx, pptx, xlsx, pdf, images, html, csv, zip...) vs PDF only",
    "What it optimizes for": "Breadth, one converter for many formats vs depth on PDF layout/OCR/forms",
    "Output": "Markdown, generally simpler vs Markdown/text with more structural detail",
    "Typical use": "Mixed source formats into an LLM or RAG index vs PDF-heavy pipelines needing layout accuracy",
}


def main() -> None:
    print("MarkItDown (this course) vs LiteParse (lessons/liteparse/):")
    for aspect, comparison in MARKITDOWN_VS_LITEPARSE.items():
        print(f"  {aspect}: {comparison}")

    # Confirm the package is installed, and which extras came with it.
    # markitdown[all] pulls in extra dependencies (pdfminer, python-docx,
    # python-pptx, openpyxl, and others) that the base `markitdown` package
    # does not install on its own. If you only `pip install markitdown`,
    # converting a PDF or docx raises MissingDependencyException naming the
    # extra you're missing, not a generic import error.
    version = importlib.metadata.version("markitdown")
    print(f"\nmarkitdown version installed: {version}")

    from markitdown import MarkItDown

    # Constructing MarkItDown() with no arguments registers every built-in
    # converter that has its dependencies satisfied. If markitdown[all]
    # weren't installed, this line would still succeed, individual
    # converters just wouldn't be able to run yet.
    md = MarkItDown()
    print("MarkItDown() constructed successfully, ready to convert.")
    print(f"Converter count: {len(md._converters)}")


if __name__ == "__main__":
    main()
