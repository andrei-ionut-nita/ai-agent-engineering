"""
Lesson 3: run types, metadata, and tags.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/01_beginner/03_types_of_runs/lesson.py
"""

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import traceable

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


# run_type tells LangSmith what kind of step this is, so the UI can
# render it differently (a "retriever" run shows documents, a "tool" run
# shows a function call, an "llm" run shows a prompt/completion pair).
# The default run_type, used when you don't pass one, is "chain".
@traceable(run_type="retriever")
def fake_search(query: str) -> list[str]:
    # Stands in for a real vector store lookup, so this lesson doesn't
    # need any extra setup. Lesson 8 introduces a real retriever.
    documents = {
        "langsmith": "LangSmith is a platform for tracing and evaluating LLM apps.",
        "langgraph": "LangGraph is a library for building stateful, graph-based agents.",
    }
    return [text for key, text in documents.items() if key in query.lower()]


@traceable(run_type="tool")
def word_count(text: str) -> int:
    return len(text.split())


# metadata and tags are extra, searchable information you attach to a
# run: metadata is free-form key/value data, tags are short labels for
# filtering (Lesson 18 covers filtering by both in depth).
@traceable(
    run_type="chain",
    metadata={"lesson": 3, "topic": "run types"},
    tags=["beginner", "langsmith-course"],
)
def answer_question(question: str) -> dict:
    docs = fake_search(question)
    context = " ".join(docs) if docs else "No matching documents."
    response = model.invoke(f"Using this context: {context}\n\nAnswer: {question}")
    return {
        "context_word_count": word_count(context),
        "answer": response.text,
    }


def main() -> None:
    result = answer_question("What is LangSmith?")
    print(result["answer"])


if __name__ == "__main__":
    main()
