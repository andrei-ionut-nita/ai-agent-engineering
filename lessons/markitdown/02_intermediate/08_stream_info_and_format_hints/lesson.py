"""
Lesson 8: StreamInfo and format hints.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/markitdown/02_intermediate/08_stream_info_and_format_hints/lesson.py

Lesson 4 passed file_extension=".docx" to convert_stream() without
explaining much about it. This lesson looks at what that hint actually
does, when MarkItDown can figure the format out without it, and what
happens when a hint is flat-out wrong: it doesn't raise an error, it
silently produces a worse conversion. That's the real reason to
understand StreamInfo, not because auto-detection is unreliable, but
because a wrong hint fails silently instead of loudly.
"""

import io

from markitdown import MarkItDown
from markitdown._stream_info import StreamInfo

# Plain CSV bytes, no filename or extension attached, this is the shape
# of data you'd have after e.g. reading a database BLOB column or an
# in-memory buffer with no filesystem path at all.
CSV_BYTES = b"Date,Category,Amount\n2026-06-02,Travel,412.50\n2026-06-03,Meals,96.20\n"


def main() -> None:
    md = MarkItDown()

    # --- No hint at all. MarkItDown's auto-detection uses `magika`
    # (a small ML-based content classifier) to guess the format directly
    # from the bytes when there's no extension or mimetype to go on. For
    # a well-formed CSV, magika correctly identifies it as CSV, and the
    # CsvConverter turns it into a proper Markdown table.
    print("=== No hint: magika content-detection alone ===\n")
    result_no_hint = md.convert_stream(io.BytesIO(CSV_BYTES))
    print(result_no_hint.markdown)

    # --- A correct hint. Same outcome as no hint here, since magika
    # already got it right, but this is the explicit, unambiguous version:
    # you're telling MarkItDown what the format is instead of asking it to
    # guess.
    print("\n=== Correct hint: file_extension='.csv' ===\n")
    result_correct_hint = md.convert_stream(io.BytesIO(CSV_BYTES), file_extension=".csv")
    print(result_correct_hint.markdown)

    # --- A WRONG hint. This is the part worth paying attention to: passing
    # file_extension=".txt" doesn't raise an error, MarkItDown trusts the
    # hint over its own content-detection and routes the file to
    # PlainTextConverter instead of CsvConverter. The conversion "succeeds"
    # completely silently, it just produces raw comma-separated text
    # instead of a Markdown table, with all the row/column structure lost.
    print("\n=== WRONG hint: file_extension='.txt' (silently loses structure) ===\n")
    result_wrong_hint = md.convert_stream(io.BytesIO(CSV_BYTES), file_extension=".txt")
    print(result_wrong_hint.markdown)

    # --- The fuller StreamInfo object. file_extension is really shorthand
    # for building a StreamInfo under the hood; StreamInfo lets you set
    # mimetype, extension, charset, and filename together, useful when
    # you have more than one piece of metadata available (e.g. a
    # Content-Type header from an HTTP upload AND a filename from a
    # Content-Disposition header).
    print("\n=== Explicit StreamInfo: mimetype + extension + filename ===\n")
    stream_info = StreamInfo(
        mimetype="text/csv",
        extension=".csv",
        filename="expenses.csv",
    )
    result_stream_info = md.convert_stream(io.BytesIO(CSV_BYTES), stream_info=stream_info)
    print(result_stream_info.markdown)


if __name__ == "__main__":
    main()
