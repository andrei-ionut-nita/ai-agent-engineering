"""
Lesson 1: what is LiteParse, and is it actually installed and working.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/liteparse/01_beginner/01_what_is_liteparse/lesson.py

Every document-parsing tool this repo has touched so far (LlamaParse-style
hosted APIs, cloud OCR services) sends your file over the internet to
someone else's server and gets structured text back. LiteParse is the
opposite: it's a Python package with a Rust extension module compiled
inside it, so parsing happens as a local function call, in this process,
on this machine, with no network request and no API key.
"""

import time

import liteparse

CLOUD_VS_LOCAL_PARSING = {
    "Where it runs": "A hosted parsing service (cloud) vs this process, in-memory (local)",
    "Network required": "Yes, every call, plus a file upload vs no, never",
    "API key required": "Yes vs no, it's just a Python import",
    "Cost": "Per-page or per-document pricing vs free, open source",
    "Privacy": "Your PDF leaves your machine vs it never does",
    "Speed": "Bounded by upload size and provider queue vs bounded by your CPU",
}


def main() -> None:
    print("Cloud document-parsing APIs vs LiteParse (this course):")
    for aspect, comparison in CLOUD_VS_LOCAL_PARSING.items():
        print(f"  {aspect}: {comparison}")

    # liteparse ships as a regular pip/uv dependency (see pyproject.toml),
    # already synced into this project's .venv. There is no separate
    # application to install and no background service to start, unlike
    # the ollama course: `import liteparse` is the entire setup.
    print(f"\nliteparse version: {liteparse.__version__}")

    # The parser itself is a Rust extension module (a compiled .so file)
    # wrapped in a thin Python API. That's what "Rust-backed" means in
    # practice: the actual PDF parsing, text extraction, and (optionally)
    # OCR happen in compiled native code, not interpreted Python, which is
    # why LiteParse can parse a page in single-digit milliseconds instead
    # of the hundreds of milliseconds a pure-Python PDF library often takes.
    start = time.perf_counter()
    parser = liteparse.LiteParse(ocr_enabled=False, quiet=True)
    result = parser.parse("lessons/liteparse/sample_data/employee_handbook.pdf")
    elapsed_ms = (time.perf_counter() - start) * 1000

    print(f"\nParsed employee_handbook.pdf in {elapsed_ms:.1f}ms, no network call made:")
    print(f"  {result.num_pages} page(s), {len(result.text)} characters extracted")


if __name__ == "__main__":
    main()
