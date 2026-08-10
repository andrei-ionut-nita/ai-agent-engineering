"""
Lesson 7: plugins and custom converters.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/markitdown/02_intermediate/07_plugins_and_custom_converters/lesson.py

Every converter MarkItDown uses, docx, pptx, xlsx, pdf, images, is the
same kind of object: a DocumentConverter subclass with an accepts()
method (should this converter handle this file?) and a convert()
method (turn it into Markdown). MarkItDown doesn't have a hardcoded
list of "supported formats", it's a registry of these objects, and
register_converter() lets you add your own.

This lesson invents a trivial synthetic format, a ".ticket" file (a
handful of "key: value" lines, like a tiny support-ticket record) that
MarkItDown has never heard of, and writes a converter for it from
scratch, confirmed against the real interface in
markitdown/_base_converter.py.
"""

import io
from pathlib import Path
from typing import Any, BinaryIO

from markitdown import MarkItDown
from markitdown._base_converter import DocumentConverter, DocumentConverterResult
from markitdown._stream_info import StreamInfo

DATA_DIR = Path(__file__).parent / "data"


class TicketConverter(DocumentConverter):
    """Converts a trivial ".ticket" format ("key: value" lines) to Markdown."""

    def accepts(
        self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs: Any
    ) -> bool:
        # accepts() should be a quick, cheap check, MarkItDown calls this
        # on every registered converter to find which one(s) claim they can
        # handle a given file, before actually running convert(). Here it's
        # just an extension check; nothing in .ticket's content needs
        # peeking at to decide.
        return (stream_info.extension or "").lower() == ".ticket"

    def convert(
        self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs: Any
    ) -> DocumentConverterResult:
        # Only called after accepts() returned True. file_stream is the
        # same open stream accepts() saw, MarkItDown doesn't re-open it.
        raw = file_stream.read().decode("utf-8")

        lines = []
        for line in raw.strip().splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                lines.append(f"- **{key.strip()}**: {value.strip()}")

        return DocumentConverterResult(
            markdown="\n".join(lines),
            title="Support Ticket",
        )


def main() -> None:
    md = MarkItDown()

    # Before registering: MarkItDown has no converter that specifically
    # claims ".ticket", but it isn't a total dead end either. The built-in
    # PlainTextConverter accepts a broad range of text-ish content as a
    # fallback (it's registered with low priority so more specific
    # converters get first refusal), so a .ticket file, being valid UTF-8
    # text, still "converts": the raw "key: value" lines pass through
    # untouched, with none of the structure a real converter would add.
    sample_bytes = (DATA_DIR / "sample_ticket.ticket").read_bytes()

    print("=== Before registering TicketConverter (falls back to plain text) ===\n")
    fallback_result = md.convert_stream(io.BytesIO(sample_bytes), file_extension=".ticket")
    print(f"Title: {fallback_result.title}")
    print("Markdown:")
    print(fallback_result.markdown)
    print()

    # register_converter() adds the converter to MarkItDown's internal
    # registry. Custom converters are inserted ahead of previously
    # registered ones by default (see the priority docs in
    # markitdown/_markitdown.py), so a custom converter can even override
    # a built-in one for formats MarkItDown already knows, not just add
    # new ones.
    md.register_converter(TicketConverter())

    print("=== After registering TicketConverter ===\n")
    result = md.convert_stream(io.BytesIO(sample_bytes), file_extension=".ticket")
    print(f"Title: {result.title}")
    print("Markdown:")
    print(result.markdown)


if __name__ == "__main__":
    main()
