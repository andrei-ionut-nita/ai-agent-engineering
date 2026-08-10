"""
Lesson 13: parsing PDFs with LiteParse, wrapping them into LlamaIndex
Documents, and querying a VectorStoreIndex built from them.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/liteparse/03_advanced/13_feeding_liteparse_into_llamaindex/lesson.py

This is the payoff lesson: everything so far has been about getting
clean text OUT of PDFs. This lesson shows what that text is actually
for, feeding it into LlamaIndex (this repo's llamaindex course, Lessons
1-4) to build a queryable index, entirely offline for the parsing step,
with only the final query going to Gemini. No hosted parsing API is
involved anywhere in this pipeline.
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


def main() -> None:
    # Step 1: LiteParse, entirely local, no network call. Every native-
    # text PDF in sample_data/ gets turned into a LlamaIndex Document.
    # scanned_notice.pdf is skipped here on purpose (ocr_enabled=False
    # would return it empty, and an empty Document adds nothing useful
    # to the index); Lesson 14's capstone handles the OCR-fallback case.
    parser = liteparse.LiteParse(ocr_enabled=False, quiet=True)
    pdf_paths = sorted(p for p in SAMPLE_DATA_DIR.glob("*.pdf") if p.name != "scanned_notice.pdf")

    documents = []
    for pdf_path in pdf_paths:
        result = parser.parse(pdf_path)
        # metadata={"source": ...} carries the originating filename
        # through the index, so a later query result can cite which
        # document it came from, the same idea as a page number in
        # Lesson 4, just at the whole-document level here.
        documents.append(Document(text=result.text, metadata={"source": pdf_path.name}))

    print(f"Parsed {len(documents)} PDF(s) locally with LiteParse, no network call:")
    for doc in documents:
        print(f"  {doc.metadata['source']}: {len(doc.text)} characters")

    # Step 2: LlamaIndex, this is where Gemini enters, for embeddings
    # and for answering the query, not for parsing the PDFs.
    Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
    Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)

    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()

    # A couple of targeted questions, each answerable from a different
    # source document, to show the index is actually retrieving across
    # documents rather than just echoing one of them.
    questions = [
        "What are the brightness levels of the Aurora Desk Lamp?",
        "How many paid vacation days do full-time employees accrue per year?",
    ]

    for question in questions:
        response = query_engine.query(question)
        print(f"\nQ: {question}")
        print(f"A: {response}")
        sources = {node.metadata.get("source") for node in response.source_nodes}
        print(f"   (retrieved from: {', '.join(sorted(sources))})")


if __name__ == "__main__":
    main()
