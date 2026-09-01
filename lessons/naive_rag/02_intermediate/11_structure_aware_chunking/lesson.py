"""
Lesson 11: chunking on a document's own structure instead of a fixed size.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/02_intermediate/11_structure_aware_chunking/lesson.py
"""

from pathlib import Path

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

# Concatenated the same way multiple source files often get combined
# into one document before chunking.
SOURCE_FILES = ["weather-station.md", "bookshelf.md", "cello-practice.md"]


def structure_aware_chunks(text: str) -> list[str]:
    lines = text.splitlines()
    chunks: list[str] = []
    current: list[str] = []

    for line in lines:
        # A Markdown heading starts a brand new chunk. Anything already
        # collected under the previous heading is finished at this
        # point, save it before starting the next one.
        if line.startswith("#") and current:
            chunks.append("\n".join(current).strip())
            current = []
        current.append(line)

    if current:
        chunks.append("\n".join(current).strip())

    return chunks


def main() -> None:
    combined_text = "\n\n".join((NOTES_DIR / name).read_text() for name in SOURCE_FILES)

    fixed_size = [combined_text[i : i + 150] for i in range(0, len(combined_text), 150)]
    structured = structure_aware_chunks(combined_text)

    print(f"Fixed-size (150 chars, no regard for structure): {len(fixed_size)} chunks\n")
    for i, chunk in enumerate(fixed_size, start=1):
        print(f"  Chunk {i}: {chunk!r}")

    print(f"\nStructure-aware (one chunk per heading): {len(structured)} chunks\n")
    for i, chunk in enumerate(structured, start=1):
        heading = chunk.splitlines()[0]
        print(f"  Chunk {i} ({len(chunk)} characters): {heading}")


if __name__ == "__main__":
    main()
