"""
Lesson 4: splitting one document into small, retrievable passages.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/01_beginner/04_chunking_a_document/lesson.py
"""

from pathlib import Path

# This course's own fixture notes, used throughout the Beginner tier as
# one combined document, the way several short files often get
# concatenated before chunking. Lesson 12 comes back to these same five
# files and treats them as separate documents instead.
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


def load_combined_document() -> str:
    # Each file opens with a "# Title" heading (Markdown structure is
    # Lesson 11's subject, not this one) and its own internal line
    # wrapping. " ".join(body.split()) drops both: it collapses every
    # run of whitespace, including the newlines between a file's own
    # paragraphs, down to single spaces, so each file becomes exactly
    # one paragraph-sized block once combined below.
    paths = sorted(NOTES_DIR.glob("*.md"))
    blocks = []
    for path in paths:
        _heading, body = path.read_text().split("\n\n", 1)
        blocks.append(" ".join(body.split()))

    # Joining with a blank line between blocks recreates the same
    # "topics separated by a blank line" shape a single hand-written
    # notes file would have.
    return "\n\n".join(blocks)


def chunk_by_paragraph(text: str) -> list[str]:
    # The combined document separates each topic with a blank line, so
    # splitting on two newlines in a row gives one chunk per topic,
    # exactly the unit a question is likely to be answered by.
    raw_chunks = text.split("\n\n")
    # Strip leading/trailing whitespace and drop any empty pieces left
    # over from trailing blank lines at the end of the file.
    return [chunk.strip() for chunk in raw_chunks if chunk.strip()]


def main() -> None:
    text = load_combined_document()
    chunks = chunk_by_paragraph(text)

    print(f"Split into {len(chunks)} chunks:\n")
    for i, chunk in enumerate(chunks, start=1):
        preview = chunk[:70]
        print(f"  Chunk {i} ({len(chunk)} characters): {preview}...")


if __name__ == "__main__":
    main()
