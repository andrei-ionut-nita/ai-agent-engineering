"""
Lesson 10: feeding MarkItDown output into LlamaIndex.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/markitdown/03_advanced/10_feeding_markitdown_into_llamaindex/lesson.py

Every lesson so far ended with converted Markdown printed to a
terminal or written to a file. This lesson takes the natural next
step: hand that Markdown to LlamaIndex (lessons/llamaindex/), build a
VectorStoreIndex over several converted documents, and query across
all of them. This assumes basic familiarity with
lessons/llamaindex/01_beginner/ Lessons 1-4 (Settings, Document,
VectorStoreIndex, query engines), see that course for what each piece
means in more depth.

Makes real Gemini API calls (embeddings for indexing, generation for
the query answer), keep that in mind against a constrained quota.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex, Document
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from markitdown import MarkItDown

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"

# The same Gemini models used throughout lessons/llamaindex/, confirmed
# working against this project's API key.
Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(
    model_name="models/gemini-embedding-001", api_key=API_KEY
)

# office_notice.png is left out here, same reasoning as Lesson 5: without
# an LLM-captioning client attached to THIS MarkItDown instance, it would
# convert to almost nothing useful. Lesson 12's capstone brings it back in
# with captioning wired up.
SOURCE_FILES = [
    "remote_work_memo.docx",
    "onboarding_deck.pptx",
    "expense_report.xlsx",
    "product_spec.pdf",
    "release_notes.txt",
]


def main() -> None:
    md = MarkItDown()

    # Convert each fixture to Markdown, then wrap it in a LlamaIndex
    # Document. This is the entire integration: MarkItDown's job ends at
    # producing a string, LlamaIndex's job starts at accepting one.
    # metadata={"source": ...} keeps track of which original file each
    # chunk came from, the same way lessons/llamaindex/'s SimpleDirectoryReader
    # attaches a file_name to every Document it loads.
    documents = []
    for filename in SOURCE_FILES:
        result = md.convert(FIXTURES_DIR / filename)
        documents.append(Document(text=result.markdown, metadata={"source": filename}))

    print(f"Converted {len(documents)} fixtures into LlamaIndex Documents.\n")

    # From here on, this is exactly lessons/llamaindex/'s core loop:
    # Documents -> VectorStoreIndex -> QueryEngine -> query(). MarkItDown's
    # involvement already ended, the index has no idea its input text
    # came from a docx, a pptx, or a plain .txt file, it's just text with
    # metadata now.
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()

    questions = [
        "What equipment stipend is available for remote workers, and what does it cover?",
        "What is the TrailLight lantern's battery life requirement?",
    ]

    for question in questions:
        response = query_engine.query(question)
        print(f"Q: {question}")
        print(f"A: {response.response}\n")

        print("  Source documents used:")
        for node in response.source_nodes:
            source = node.metadata.get("source", "unknown")
            print(f"    - {source} (score={node.score:.4f})")
        print()


if __name__ == "__main__":
    main()
