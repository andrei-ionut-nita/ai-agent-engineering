"""Lesson 16: feeding docling's HybridChunker output into LlamaIndex.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/docling/03_advanced/16_feeding_docling_into_llamaindex/lesson.py

Lesson 11 chunked a DoclingDocument with HybridChunker and stopped at
printing the chunks. This lesson takes the natural next step: hand
those chunks to LlamaIndex (lessons/llamaindex/) as Documents, build a
VectorStoreIndex, and query across all of them. This assumes basic
familiarity with lessons/llamaindex/01_beginner/ Lessons 1-4 (Settings,
Document, VectorStoreIndex, query engines), see that course for what
each piece means in more depth.

Makes real Gemini API calls (embeddings for indexing, generation for
the query answer), keep that in mind against a constrained quota.
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

# The same Gemini models used throughout lessons/llamaindex/, confirmed
# working against this project's API key.
Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)

SOURCE_FILES = ["quarterly_report.pdf", "project_plan.docx", "team_update.pptx"]


def main() -> None:
    converter = DocumentConverter()
    chunker = HybridChunker()

    # Convert each fixture, chunk it with HybridChunker, then wrap each
    # chunk in a LlamaIndex Document. This is the entire integration:
    # docling's job ends at producing structured, contextualized chunk
    # text, LlamaIndex's job starts at accepting Documents. One chunk
    # per Document, rather than one Document per file, keeps LlamaIndex's
    # own retrieval granularity aligned with docling's structural
    # chunk boundaries instead of re-splitting whole-file text itself.
    documents = []
    for filename in SOURCE_FILES:
        result = converter.convert(SAMPLE_DATA / filename)
        for chunk in chunker.chunk(dl_doc=result.document):
            documents.append(
                Document(
                    text=chunker.contextualize(chunk=chunk),
                    metadata={"source": filename, "headings": chunk.meta.headings},
                )
            )

    print(f"Converted {len(SOURCE_FILES)} fixtures into {len(documents)} LlamaIndex Documents.\n")

    # From here on, this is exactly lessons/llamaindex/'s core loop:
    # Documents -> VectorStoreIndex -> QueryEngine -> query(). Docling's
    # involvement already ended, the index has no idea its input text
    # came from a docling chunk rather than a plain text file.
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()

    questions = [
        "How much did North region hardware revenue grow in Q3?",
        "What is the main risk in the warehouse automation rollout?",
    ]

    for question in questions:
        response = query_engine.query(question)
        print(f"Q: {question}")
        print(f"A: {response}\n")


if __name__ == "__main__":
    main()
