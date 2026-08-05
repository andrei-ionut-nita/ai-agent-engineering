"""
Lesson 21: a full RAG pipeline, backed by a Postgres vector store that
survives a restart, run this script twice to see the difference.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/03_advanced/21_persistent_rag_pipeline/lesson.py
"""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

NOTES_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "langchain"
    / "03_advanced"
    / "27_document_loading_and_splitting"
    / "data"
    / "notes.txt"
)
EMBEDDING_DIMENSIONS = 768
COLLECTION_NAME = "notes_persistent"


def already_ingested(dsn: str, collection_name: str) -> bool:
    with psycopg.connect(dsn) as conn:
        row = conn.execute(
            """
            SELECT count(*) FROM langchain_pg_embedding e
            JOIN langchain_pg_collection c ON c.uuid = e.collection_id
            WHERE c.name = %s
            """,
            (collection_name,),
        ).fetchone()
        return row[0] > 0


def load_and_split() -> list[Document]:
    text = NOTES_PATH.read_text()
    document = Document(page_content=text, metadata={"source": str(NOTES_PATH)})
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    return splitter.split_documents([document])


def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def main() -> None:
    dsn_raw = os.environ["POSTGRES_DSN"]
    dsn_sqlalchemy = dsn_raw.replace("postgresql://", "postgresql+psycopg://")

    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        output_dimensionality=EMBEDDING_DIMENSIONS,
    )
    vector_store = PGVector(
        embeddings=embeddings_model,
        connection=dsn_sqlalchemy,
        collection_name=COLLECTION_NAME,
    )

    if already_ingested(dsn_raw, COLLECTION_NAME):
        print("Already ingested, skipping re-embedding (this is the point).\n")
    else:
        chunks = load_and_split()
        vector_store.add_documents(chunks)
        print(f"Ingested {len(chunks)} chunks for the first time.\n")

    retriever = vector_store.as_retriever(search_kwargs={"k": 2})

    model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    prompt = ChatPromptTemplate.from_template(
        "Answer the question using only the context below.\n\n"
        "Context:\n{context}\n\nQuestion: {question}"
    )

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )

    question = "What do I know about baking bread at home?"
    answer = chain.invoke(question)

    print(f"Question: {question}")
    print(f"Answer: {answer}")


if __name__ == "__main__":
    main()
