"""
Lesson 12 (capstone): a single searchable index over every fixture format.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/markitdown/03_advanced/12_advanced_capstone_project/lesson.py

This ties together everything this course covered: Lesson 6's LLM
image captioning, Lesson 10's MarkItDown-to-LlamaIndex handoff, and
Lesson 5/9's "convert everything in this folder" loop, applied to the
FULL fixtures/ folder this time, all six files, including
office_notice.png, with captioning wired in so the image actually
contributes something an LLM can retrieve. The result is one Gemini-
backed index that can answer questions whose answers live in different
source formats: a docx, a pptx, an xlsx, a pdf, a txt, and a captioned
png, all searchable through the same query engine.

Makes real Gemini API calls: one captioning call for the image, one
embedding call per document at index time, one generation call per
question. Keep that in mind against a constrained quota, this is the
most Gemini-call-heavy lesson in the course.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex, Document
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from markitdown import MarkItDown
from openai import OpenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(
    model_name="models/gemini-embedding-001", api_key=API_KEY
)


def main() -> None:
    # Lesson 6's pattern: an OpenAI-shaped client pointed at Gemini's
    # OpenAI-compatible endpoint, attached to MarkItDown so the image
    # fixture gets a real description instead of converting to almost
    # nothing.
    caption_client = OpenAI(
        api_key=API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    md = MarkItDown(llm_client=caption_client, llm_model="gemini-3.5-flash-lite")

    # Convert every file in fixtures/, no skip list this time, the
    # captioning client makes office_notice.png worth including.
    documents = []
    for source_path in sorted(p for p in FIXTURES_DIR.iterdir() if p.is_file()):
        result = md.convert(source_path)
        documents.append(Document(text=result.markdown, metadata={"source": source_path.name}))
        print(f"Converted {source_path.name} ({len(result.markdown)} chars)")

    print(f"\nIndexing {len(documents)} documents across 6 different source formats...\n")
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()

    # Each question is answerable from a different source format,
    # confirming the index genuinely spans all of them, not just the
    # text-native ones.
    questions = [
        "When is the office closed and why?",               # answered from the captioned PNG
        "What laptop charger expense was submitted and on what date?",  # xlsx
        "What onboarding buddy meeting happens in week one?",           # pptx
    ]

    for question in questions:
        response = query_engine.query(question)
        print(f"Q: {question}")
        print(f"A: {response.response}")
        print("  Source documents used:")
        for node in response.source_nodes:
            source = node.metadata.get("source", "unknown")
            print(f"    - {source} (score={node.score:.4f})")
        print()


if __name__ == "__main__":
    main()
