"""
Lesson 5 (checkpoint): convert every fixture file to a .md file on disk.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/markitdown/01_beginner/05_beginner_checkpoint_project/lesson.py

This is the Beginner checkpoint: no new MarkItDown API, just Lessons
1-3's .convert(path) call, run in a loop over every file in fixtures/,
writing each result to disk and printing a summary table. This is the
shape of a real batch-conversion script: point it at a folder, get
Markdown files out the other side.

office_notice.png is included in the fixtures folder but skipped here
on purpose: without an LLM client, MarkItDown's image converter has no
way to describe what's in a photo, it can only report basic file
metadata. Lesson 6 revisits this exact file with LLM captioning wired
up, and shows what image conversion looks like with and without it.
"""

from pathlib import Path

from markitdown import MarkItDown

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"
OUTPUT_DIR = Path(__file__).parent / "converted"

# office_notice.png is deliberately excluded here, see the module
# docstring: without an LLM client it converts to essentially nothing
# useful, and that's Lesson 6's point to make, not this one's.
SKIP = {"office_notice.png"}


def main() -> None:
    md = MarkItDown()
    OUTPUT_DIR.mkdir(exist_ok=True)

    source_files = sorted(
        p for p in FIXTURES_DIR.iterdir() if p.is_file() and p.name not in SKIP
    )

    summary = []
    for source_path in source_files:
        result = md.convert(source_path)

        # Write each conversion result out as its own .md file, same base
        # name as the source, this is the "drop folder" pattern Lesson 9
        # builds on with custom converters and format hints.
        output_path = OUTPUT_DIR / f"{source_path.stem}.md"
        output_path.write_text(result.markdown, encoding="utf-8")

        summary.append((source_path.name, source_path.suffix, len(result.markdown)))

    print(f"Converted {len(summary)} files from fixtures/ into {OUTPUT_DIR}/\n")
    print(f"{'Source file':<28} {'Format':<8} {'Output length (chars)':>22}")
    print("-" * 60)
    for name, suffix, length in summary:
        print(f"{name:<28} {suffix:<8} {length:>22}")


if __name__ == "__main__":
    main()
