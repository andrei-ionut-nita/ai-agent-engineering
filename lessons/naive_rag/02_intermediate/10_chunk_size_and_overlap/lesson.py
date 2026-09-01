"""
Lesson 10: how chunk size and overlap change what retrieval can find.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/02_intermediate/10_chunk_size_and_overlap/lesson.py
"""

from pathlib import Path

NOTES_PATH = Path(__file__).parent.parent.parent / "fixtures" / "notes" / "weather-station.md"

CHUNK_SIZE = 110


def fixed_size_chunks(text: str, size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        # Move the window forward by (size - overlap) instead of size,
        # so the next chunk re-includes the last `overlap` characters of
        # this one, instead of starting exactly where this one ended.
        start += size - overlap
    return chunks


def find_chunk_mentioning(chunks: list[str], keyword: str) -> str | None:
    for chunk in chunks:
        if keyword in chunk:
            return chunk
    return None


def main() -> None:
    text = NOTES_PATH.read_text()

    no_overlap = fixed_size_chunks(text, size=CHUNK_SIZE, overlap=0)
    with_overlap = fixed_size_chunks(text, size=CHUNK_SIZE, overlap=30)

    print(f"No overlap: {len(no_overlap)} chunks of up to {CHUNK_SIZE} characters\n")
    for i, chunk in enumerate(no_overlap, start=1):
        print(f"  Chunk {i}: {chunk!r}")

    print(f"\nWith 30-character overlap: {len(with_overlap)} chunks\n")
    for i, chunk in enumerate(with_overlap, start=1):
        print(f"  Chunk {i}: {chunk!r}")

    print("\n--- The difference that matters ---")
    keyword = "readings"
    no_overlap_hit = find_chunk_mentioning(no_overlap, keyword)
    with_overlap_hit = find_chunk_mentioning(with_overlap, keyword)

    print(f"\nNo-overlap chunk containing the whole word {keyword!r}: {no_overlap_hit!r}")
    print(f"With-overlap chunk containing the whole word {keyword!r}: {with_overlap_hit!r}")


if __name__ == "__main__":
    main()
