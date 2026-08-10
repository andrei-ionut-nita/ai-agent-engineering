"""
Lesson 14 (Capstone): a mixed native + scanned PDF folder, parsed with
LiteParse and an OCR fallback, indexed with LlamaIndex, and queried
with Gemini. No hosted document-parsing API anywhere in this pipeline.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/liteparse/03_advanced/14_advanced_capstone_project/lesson.py

This combines the whole course: LiteParse() with ocr_enabled=False as
the fast default (Lesson 3), a text-yield OCR fallback for documents
that need it (Lesson 11), and feeding the unified result into a
LlamaIndex VectorStoreIndex queried with Gemini (Lesson 13). Every PDF
in sample_data/, native and scanned alike, ends up queryable together.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

import liteparse

load_dotenv()

SAMPLE_DATA_DIR = Path("lessons/liteparse/sample_data")
API_KEY = os.environ["GOOGLE_API_KEY"]
NEAR_ZERO_TEXT_CHARS = 20


def parse_folder_with_ocr_fallback(folder: Path) -> list[Document]:
    """Parse every PDF in `folder`, falling back to OCR only for the
    documents whose fast, OCR-off parse yields near-zero text (Lesson 11)."""
    parser_no_ocr = liteparse.LiteParse(ocr_enabled=False, quiet=True)
    parser_ocr = liteparse.LiteParse(ocr_enabled=True, quiet=True)

    documents = []
    for pdf_path in sorted(folder.glob("*.pdf")):
        result = parser_no_ocr.parse(pdf_path)
        used_ocr = False

        if len(result.text.strip()) < NEAR_ZERO_TEXT_CHARS:
            result = parser_ocr.parse(pdf_path)
            used_ocr = True

        print(f"  {pdf_path.name}: {len(result.text)} chars (ocr_used={used_ocr})")
        documents.append(Document(text=result.text, metadata={"source": pdf_path.name, "ocr_used": used_ocr}))

    return documents


def main() -> None:
    print("Stage 1: LiteParse, local, no network, OCR only where the fast pass yielded near-zero text:")
    documents = parse_folder_with_ocr_fallback(SAMPLE_DATA_DIR)

    total_chars = sum(len(d.text) for d in documents)
    ocr_count = sum(1 for d in documents if d.metadata["ocr_used"])
    print(f"\n{len(documents)} document(s) parsed, {total_chars} total characters, {ocr_count} needed OCR")

    print("\nStage 2: LlamaIndex + Gemini, indexing and querying (the only network calls in this pipeline):")
    Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
    Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)

    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()

    # Three questions, deliberately spanning three different source
    # documents, INCLUDING one whose answer only exists because of the
    # OCR fallback: scanned_notice.pdf has no native text at all
    # (Lesson 8), so without Stage 1's fallback, this last question
    # would have nothing to retrieve an answer from.
    questions = [
        "What are the brightness levels of the Aurora Desk Lamp?",
        "How many paid vacation days do full-time employees accrue per year?",
        "What time will water service be interrupted, according to the building notice?",
    ]

    for question in questions:
        response = query_engine.query(question)
        sources = {node.metadata.get("source") for node in response.source_nodes}
        print(f"\nQ: {question}")
        print(f"A: {response}")
        print(f"   (retrieved from: {', '.join(sorted(sources))})")


if __name__ == "__main__":
    main()
