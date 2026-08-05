"""
Lesson 28: embeddings and a vector store, making text searchable by meaning.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/03_advanced/28_rag_embeddings_and_vectorstore/lesson.py

Builds on Lesson 27: same notes.txt, loaded and split the same way.
This lesson turns those chunks into something you can search by MEANING,
not just by matching exact words.
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

NOTES_PATH = Path(__file__).parent.parent / "27_document_loading_and_splitting" / "data" / "notes.txt"


def load_and_split() -> list[Document]:
    text = NOTES_PATH.read_text()
    document = Document(page_content=text, metadata={"source": str(NOTES_PATH)})
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    return splitter.split_documents([document])


def main() -> None:
    chunks = load_and_split()

    # An embeddings model turns text into a long list of numbers (a
    # "vector"), positioned so that texts with SIMILAR MEANING end up
    # with similar numbers, close together in that number-space, even if
    # they don't share any exact words.
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    # InMemoryVectorStore stores each chunk's text alongside its
    # embedding vector, and knows how to find the closest ones to a new
    # query, entirely in memory, no external database needed for this
    # lesson.
    vector_store = InMemoryVectorStore(embeddings_model)
    vector_store.add_documents(chunks)

    # Notice: this question shares almost NO exact words with the
    # matching chunk ("Recipe notes... pizza dough... yeast..."). A
    # plain keyword search for "baking bread at home" wouldn't find it.
    # But the MEANING is close, and that's what similarity search finds.
    query = "What do I know about baking bread at home?"
    results = vector_store.similarity_search(query, k=2)

    print(f"Query: {query}\n")
    print(f"Top {len(results)} most similar chunks:\n")
    for i, result in enumerate(results):
        print(f"--- Match {i + 1} ---")
        print(result.page_content.strip())
        print()


if __name__ == "__main__":
    main()
