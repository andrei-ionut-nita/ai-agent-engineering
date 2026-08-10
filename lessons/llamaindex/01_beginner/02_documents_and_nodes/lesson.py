"""
Lesson 2: Document and Node, LlamaIndex's two most basic building blocks.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/01_beginner/02_documents_and_nodes/lesson.py

No LLM or embedding calls yet, splitting text into Nodes is pure local
computation. This is the same idea as Lesson 27 in lessons/langchain
(Document + RecursiveCharacterTextSplitter), just in LlamaIndex's own
vocabulary.
"""

from pathlib import Path

# SimpleDirectoryReader is LlamaIndex's most common document loader: point
# it at a folder, and it reads every file in it (.txt, .pdf, .md, and
# more), wrapping each one as a Document.
from llama_index.core import SimpleDirectoryReader

# SentenceSplitter breaks a Document's text into smaller Node objects,
# trying to break on sentence boundaries rather than mid-sentence. It's
# LlamaIndex's rough equivalent of LangChain's RecursiveCharacterTextSplitter.
from llama_index.core.node_parser import SentenceSplitter

DATA_DIR = Path(__file__).parent / "data"


def main() -> None:
    # SimpleDirectoryReader().load_data() reads every file in DATA_DIR and
    # returns a list of Document objects. A Document bundles raw text
    # (.text) with metadata about where it came from (.metadata), the same
    # idea as LangChain's Document(page_content=..., metadata=...).
    documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()

    print(f"Loaded {len(documents)} documents from {DATA_DIR.name}/:\n")
    for doc in documents:
        source = Path(doc.metadata["file_name"]).name
        print(f"  {source}: {len(doc.text)} characters")

    # A Node is what you get after splitting a Document into a smaller
    # chunk. Where a Document is "one whole file," a Node is "one
    # searchable piece of it," the actual unit an Index stores and
    # retrieves. Each Node carries: the chunk's text, metadata inherited
    # from its parent Document, and relationships to its neighboring
    # Nodes (which came before/after it in the original Document), so an
    # index can, if needed, pull in surrounding context around a match.
    splitter = SentenceSplitter(chunk_size=200, chunk_overlap=20)
    nodes = splitter.get_nodes_from_documents(documents)

    print(f"\nSplit into {len(nodes)} nodes:\n")
    for i, node in enumerate(nodes):
        source = Path(node.metadata["file_name"]).name
        print(f"--- Node {i} (from {source}, {len(node.text)} chars) ---")
        print(node.text.strip())
        print()

    # Inspect one Node up close: text, metadata, and relationships all
    # live on the same object.
    first_node = nodes[0]
    print("First node's attributes:")
    print(f"  node_id: {first_node.node_id[:8]}...")
    print(f"  metadata keys: {sorted(first_node.metadata.keys())}")
    print(f"  relationships: {sorted(r.name for r in first_node.relationships)}")


if __name__ == "__main__":
    main()
