"""
Lesson 21: retrieval-augmented generation, embedding through answer, all local.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/03_advanced/21_local_rag_with_ollama/lesson.py

Uses the same notes.txt the langchain course's Lesson 27 loads and
splits, and the same cosine-similarity idea from Lesson 8 of this
course, chained together into the full RAG pipeline: split, embed,
retrieve, generate. The pgvector course does the retrieval step with a
real database instead of plain Python; this lesson keeps it simple and
in-memory so the focus stays on Ollama end to end.
"""

import math
from pathlib import Path

import ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter

NOTES_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "langchain"
    / "03_advanced"
    / "27_document_loading_and_splitting"
    / "data"
    / "notes.txt"
)

QUESTION = "What instrument is being practiced?"


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot_product / (norm_a * norm_b)


def main() -> None:
    # Split: same RecursiveCharacterTextSplitter as langchain Lesson 27,
    # breaking the notes into a handful of topic-sized chunks.
    text = NOTES_PATH.read_text()
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    chunks = splitter.split_text(text)
    print(f"Split notes.txt into {len(chunks)} chunks.\n")

    # Embed: every chunk, in one batched call, exactly like Lesson 8.
    chunk_embeddings = ollama.embed(model="nomic-embed-text", input=chunks).embeddings

    # Retrieve: embed the question the same way, then rank every chunk by
    # how similar its meaning is to the question's meaning, no keyword
    # matching involved at all.
    question_embedding = ollama.embed(model="nomic-embed-text", input=[QUESTION]).embeddings[0]
    ranked = sorted(
        zip(chunks, chunk_embeddings),
        key=lambda pair: cosine_similarity(question_embedding, pair[1]),
        reverse=True,
    )
    best_chunk = ranked[0][0]
    print(f"Question: {QUESTION}")
    print(f"Most relevant chunk:\n{best_chunk}\n")

    # Generate: hand only the retrieved chunk to the model as context, not
    # the whole document. This is the entire point of retrieval: keeping
    # the model's actual input small and relevant, instead of stuffing
    # everything you know into every prompt.
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": "Answer using only the provided context. If the answer is not in the context, say you do not know.",
            },
            {"role": "user", "content": f"Context:\n{best_chunk}\n\nQuestion: {QUESTION}"},
        ],
        options={"temperature": 0},
    )
    print(f"Answer: {response.message.content}")


if __name__ == "__main__":
    main()
