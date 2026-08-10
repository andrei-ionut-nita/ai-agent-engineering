"""
Lesson 4: converting from an open file stream, and from a URL.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/markitdown/01_beginner/04_converting_from_streams_and_urls/lesson.py

Every lesson so far called .convert() on a file path. Real pipelines
often don't have a path at all: a file uploaded to a web server arrives
as an in-memory stream, and a lot of useful content lives on the web,
not on disk. This lesson covers both of MarkItDown's other entry
points: convert_stream() and convert_url().

Note: convert_url() makes a real network request to a live public
site. If books.toscrape.com is unreachable, that call will raise an
exception unrelated to MarkItDown itself, this course chose it for the
same reason lessons/playwright/01_beginner/04_navigating_to_a_page/
did: it's a stable, public test site built for exactly this purpose.
"""

from pathlib import Path

from markitdown import MarkItDown

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"


def main() -> None:
    md = MarkItDown()

    # --- convert_stream(): the same conversion, from an open file handle
    # instead of a path. This is the shape you'd use if the file arrived
    # over HTTP (e.g. a Flask/FastAPI upload) and never touched disk as a
    # named file, only as bytes in memory.
    print("=== convert_stream() on remote_work_memo.docx ===\n")
    docx_path = FIXTURES_DIR / "remote_work_memo.docx"
    with open(docx_path, "rb") as f:
        # A raw binary stream has no filename or extension attached to it,
        # so unlike .convert(path), auto-detection has nothing to go on
        # unless you tell it. file_extension is the simplest hint, Lesson 8
        # covers the fuller StreamInfo API for cases where even the
        # extension isn't known up front.
        stream_result = md.convert_stream(f, file_extension=".docx")

    print(stream_result.markdown[:200])
    print("...\n")

    # --- convert_url(): fetches a live web page and converts its HTML to
    # Markdown. Under the hood this is still just "get bytes, then
    # convert", the bytes just come from an HTTP GET instead of a local
    # file.
    print("=== convert_url() on https://books.toscrape.com/ ===\n")
    url_result = md.convert_url("https://books.toscrape.com/")

    print(f"Converted length: {len(url_result.markdown)} characters")
    print("First 400 characters:\n")
    print(url_result.markdown[:400])


if __name__ == "__main__":
    main()
