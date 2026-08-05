"""
Lesson 27: loading a document and splitting it into chunks.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/03_advanced/27_document_loading_and_splitting/lesson.py

This lesson doesn't call the model at all. It's pure setup work for
Lessons 28-29 (RAG): reading a real text file, wrapping it as a
LangChain Document, and splitting it into smaller pieces small enough
to search over individually.
"""

from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

NOTES_PATH = Path(__file__).parent / "data" / "notes.txt"


def load_document() -> Document:
    # A "document loader" in LangChain, at its simplest, is just: read
    # some text, and wrap it in a Document object. Document bundles the
    # raw text (page_content) together with metadata about where it
    # came from (source), which matters later when you want to know
    # which original file an answer was actually pulled from.
    text = NOTES_PATH.read_text()
    return Document(page_content=text, metadata={"source": str(NOTES_PATH)})


def main() -> None:
    document = load_document()
    print(f"Loaded document: {len(document.page_content)} characters")
    print(f"Metadata: {document.metadata}\n")

    # A text splitter breaks one long document into several smaller
    # chunks. This matters for Lesson 28: search works far better over
    # small, focused chunks (each about one topic) than over one giant
    # blob of unrelated paragraphs.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30,
    )
    chunks = splitter.split_documents([document])

    print(f"Split into {len(chunks)} chunks:\n")
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i} ({len(chunk.page_content)} chars) ---")
        print(chunk.page_content.strip())
        print()


if __name__ == "__main__":
    main()
