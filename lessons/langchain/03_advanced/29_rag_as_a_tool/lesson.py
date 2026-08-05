"""
Lesson 29: RAG as a tool, letting an agent search your documents.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/03_advanced/29_rag_as_a_tool/lesson.py

Builds on Lessons 27-28: same notes.txt, loaded, split, and embedded the
same way. This lesson wraps the similarity search as a tool (the same
@tool pattern from Lesson 13), so an agent can decide FOR ITSELF when it
needs to search your documents, instead of us always searching manually.
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

NOTES_PATH = Path(__file__).parent.parent / "27_document_loading_and_splitting" / "data" / "notes.txt"


def build_vector_store() -> InMemoryVectorStore:
    text = NOTES_PATH.read_text()
    document = Document(page_content=text, metadata={"source": str(NOTES_PATH)})
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    chunks = splitter.split_documents([document])

    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = InMemoryVectorStore(embeddings_model)
    vector_store.add_documents(chunks)
    return vector_store


vector_store = build_vector_store()


# Same @tool decorator from Lesson 13. The AI will see this tool's name
# and docstring, exactly like calculator or word_counter, and decide for
# itself when a question calls for searching personal notes.
@tool
def search_personal_notes(query: str) -> str:
    """Search the user's personal notes for information relevant to the
    query. Use this for questions about the user's projects, garden,
    recipes, hobbies, or anything that sounds like it might be
    documented in their personal notes rather than general knowledge."""
    results = vector_store.similarity_search(query, k=2)
    if not results:
        return "No relevant notes found."
    return "\n\n".join(result.page_content for result in results)


model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
agent = create_agent(
    model=model,
    tools=[search_personal_notes],
    system_prompt=(
        "You are a helpful assistant. Use the search_personal_notes tool "
        "for anything that might be in the user's personal notes."
    ),
)


def ask(question: str) -> None:
    result = agent.invoke({"messages": [HumanMessage(question)]})
    print(f"Q: {question}")
    print(f"A: {result['messages'][-1].text}\n")


def main() -> None:
    # This can ONLY be answered correctly by actually searching the
    # notes, the agent has no other way to know this.
    ask("How often do I practice my cello, and for how long?")

    # This is general knowledge, no tool needed, showing the agent still
    # knows when NOT to search (same idea as Lesson 15).
    ask("What is the capital of Japan?")


if __name__ == "__main__":
    main()
