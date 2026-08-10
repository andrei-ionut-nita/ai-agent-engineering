"""
Lesson 2: the first real .convert() call.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/markitdown/01_beginner/02_first_convert_call/lesson.py

Lesson 1 confirmed MarkItDown is installed. This lesson does the one
thing the whole library exists for: hand it a file path, get Markdown
back. Everything later in this course is a variation on this call.
"""

from pathlib import Path

from markitdown import MarkItDown

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"


def main() -> None:
    # MarkItDown() with no arguments is enough for local file conversion,
    # no API key, no network call. Lesson 6 is the first lesson that needs
    # a client (for image captioning).
    md = MarkItDown()

    # .convert() takes a path (str or Path) and returns a
    # DocumentConverterResult. It auto-detects the format from the file
    # extension and content, you don't tell it "this is a text file."
    result = md.convert(FIXTURES_DIR / "release_notes.txt")

    print("Converted: release_notes.txt")
    print(f"Result type: {type(result).__name__}")

    # .text_content and .markdown return the exact same string, .markdown
    # is the current name, .text_content is a soft-deprecated alias kept
    # for readability and backward compatibility. Either works.
    print(f"\n.text_content == .markdown: {result.text_content == result.markdown}")

    print("\nFull converted Markdown:")
    print("-" * 40)
    print(result.markdown)
    print("-" * 40)

    # .title is metadata some converters populate (docx/pptx often do, from
    # document properties) and others leave as None (plain text has no
    # concept of a title). Lesson 3 will show a case where it's populated.
    print(f"\nTitle: {result.title!r}")


if __name__ == "__main__":
    main()
