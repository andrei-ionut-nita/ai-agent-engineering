"""Lesson 18 (Advanced capstone): folder to queryable RAG index.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/03_advanced/18_advanced_capstone_project/lesson.py

This capstone introduces no new docling or LlamaIndex API. It combines
the entire course into one script:

- Lesson 15's convert_all(), reused converter across a whole folder.
- Lesson 9's OCR, needed for scanned_invoice.pdf.
- Lesson 11's HybridChunker, structure-aware chunking, not a naive split.
- Lesson 16's docling-chunk-to-LlamaIndex-Document handoff.

The difference from Lesson 16 is scope: every file in sample_data/,
five different documents across four formats (PDF native-text, PDF
image-only, DOCX, PPTX), one converter, one chunker, one index.

Makes real Gemini API calls (embeddings for indexing, generation for
each query answer), keep that in mind against a constrained quota.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

SAMPLE_DATA = Path(__file__).parent.parent.parent / "sample_data"

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)


def build_index() -> VectorStoreIndex:
    converter = DocumentConverter()
    chunker = HybridChunker()

    # Every real file in sample_data/, not a curated subset. Default
    # pipeline options handle all four formats correctly: OCR for
    # scanned_invoice.pdf's missing text layer, table structure for
    # quarterly_report.pdf, native structure reads for the DOCX and PPTX.
    source_files = sorted(p for p in SAMPLE_DATA.iterdir() if p.is_file())

    documents = []
    for source_path in source_files:
        result = converter.convert(source_path)
        for chunk in chunker.chunk(dl_doc=result.document):
            documents.append(
                Document(
                    text=chunker.contextualize(chunk=chunk),
                    metadata={"source": source_path.name},
                )
            )

    print(f"Converted {len(source_files)} files into {len(documents)} chunks.\n")
    return VectorStoreIndex.from_documents(documents)


def main() -> None:
    index = build_index()
    query_engine = index.as_query_engine()

    # Each question is answerable from a different source file, this
    # proves the index actually spans every format, not just the
    # easiest one to convert.
    questions = {
        "How much did North region hardware revenue grow in Q3?": "quarterly_report.pdf",
        "What is the main risk in the warehouse automation rollout?": "project_plan.docx",
        "What is the mitigation plan for the conveyor motor lead time risk?": "team_update.pptx",
        "What is the total due on invoice 4471?": "scanned_invoice.pdf (via OCR)",
    }

    for question, expected_source in questions.items():
        response = query_engine.query(question)
        top_sources = sorted({node.metadata.get("source") for node in response.source_nodes})
        print(f"Q: {question}")
        print(f"A: {response}")
        print(f"   (expected source: {expected_source}, retrieved from: {top_sources})\n")


if __name__ == "__main__":
    main()
