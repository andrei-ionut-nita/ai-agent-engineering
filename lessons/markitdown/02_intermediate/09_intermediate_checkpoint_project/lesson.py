"""
Lesson 9 (checkpoint): a "drop folder" converter.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/markitdown/02_intermediate/09_intermediate_checkpoint_project/lesson.py

This is the Intermediate checkpoint: combine Lesson 7's custom
converter (register_converter, for the synthetic .ticket format) with
a "convert whatever's in this folder" loop like Lesson 5's, but this
time handling the case Lesson 5 didn't have to: a file nothing can
convert. data/ here has two .ticket files (Lesson 7's custom format)
and one genuinely unsupported .bin file, a stand-in for "someone dropped
a file into this folder that doesn't correspond to any known format."
A real drop-folder script has to keep going when that happens, not
crash the whole batch.
"""

from pathlib import Path
from typing import Any, BinaryIO

from markitdown import MarkItDown
from markitdown._base_converter import DocumentConverter, DocumentConverterResult
from markitdown._exceptions import UnsupportedFormatException
from markitdown._stream_info import StreamInfo

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "converted"


class TicketConverter(DocumentConverter):
    """Converts the synthetic ".ticket" format ("key: value" lines) to Markdown.

    Same converter as Lesson 7, redefined here so this lesson stands on
    its own without importing across lesson folders.
    """

    def accepts(
        self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs: Any
    ) -> bool:
        return (stream_info.extension or "").lower() == ".ticket"

    def convert(
        self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs: Any
    ) -> DocumentConverterResult:
        raw = file_stream.read().decode("utf-8")
        lines = [
            f"- **{key.strip()}**: {value.strip()}"
            for key, _, value in (line.partition(":") for line in raw.strip().splitlines())
            if key.strip()
        ]
        return DocumentConverterResult(markdown="\n".join(lines), title="Support Ticket")


def main() -> None:
    md = MarkItDown()
    md.register_converter(TicketConverter())
    OUTPUT_DIR.mkdir(exist_ok=True)

    source_files = sorted(p for p in DATA_DIR.iterdir() if p.is_file())

    results = []
    for source_path in source_files:
        try:
            # .convert(path) still works here even though the file has no
            # extension MarkItDown was born knowing about, because
            # TicketConverter is now part of the registry and accepts()
            # matches on ".ticket" the same way it would for any built-in
            # format.
            result = md.convert(source_path)
        except UnsupportedFormatException:
            # This is the case Lesson 5's fixtures/ folder never triggered:
            # a file no registered converter, built-in or custom, claims.
            # A real drop-folder job has to keep processing the rest of the
            # batch rather than crash on the first file it can't handle.
            results.append((source_path.name, "SKIPPED (unsupported format)", 0))
            continue

        output_path = OUTPUT_DIR / f"{source_path.stem}.md"
        output_path.write_text(result.markdown, encoding="utf-8")
        results.append((source_path.name, "converted", len(result.markdown)))

    print(f"Processed {len(results)} files from data/\n")
    print(f"{'File':<24} {'Status':<28} {'Output length':>14}")
    print("-" * 68)
    for name, status, length in results:
        length_display = str(length) if status == "converted" else "-"
        print(f"{name:<24} {status:<28} {length_display:>14}")


if __name__ == "__main__":
    main()
