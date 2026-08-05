"""
Lesson 8: a small RAG app, and a dataset of examples to test it against.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/02_intermediate/08_dataset_upload/lesson.py
"""

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client, traceable

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
client = Client()

# A tiny "knowledge base": no vector store, no embeddings, just enough
# to make retrieve() do real work. Later lessons evaluate this app, so
# keeping it small keeps those evaluations easy to reason about.
DOCS = {
    "langchain": "LangChain is a framework for building LLM applications with a shared interface across model providers.",
    "langgraph": "LangGraph is a library for building stateful, graph-based agents on top of LangChain.",
    "langsmith": "LangSmith is a platform for tracing, evaluating, and monitoring LLM applications in development and production.",
}


@traceable(run_type="retriever")
def retrieve(question: str) -> list[str]:
    matches = [text for key, text in DOCS.items() if key in question.lower()]
    return matches or list(DOCS.values())


@traceable(run_type="chain")
def rag_answer(question: str) -> str:
    context = "\n".join(retrieve(question))
    response = model.invoke(
        f"Using only this context, answer in one short sentence.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )
    return response.text


# The examples this course's evaluations (Lessons 9-16) will run the app
# against. Each has a "question" input and a reference "answer", the
# ground truth an evaluator can compare the app's real answer to.
EXAMPLES = [
    {
        "inputs": {"question": "What is LangGraph used for?"},
        "outputs": {"answer": "Building stateful, graph-based agents."},
    },
    {
        "inputs": {"question": "What does LangSmith do?"},
        "outputs": {"answer": "It traces, evaluates, and monitors LLM applications."},
    },
    {
        "inputs": {"question": "What is LangChain?"},
        "outputs": {"answer": "A framework for building LLM apps across model providers."},
    },
]

DATASET_NAME = "langsmith-course-rag-qa"


def ensure_dataset() -> None:
    # has_dataset/create_dataset let this script be run more than once
    # without erroring on "dataset already exists".
    if client.has_dataset(dataset_name=DATASET_NAME):
        print(f"Dataset '{DATASET_NAME}' already exists, skipping upload.")
        return
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Q&A pairs for the langsmith course's small RAG app.",
    )
    client.create_examples(dataset_id=dataset.id, examples=EXAMPLES)
    print(f"Created dataset '{DATASET_NAME}' with {len(EXAMPLES)} examples.")


def main() -> None:
    ensure_dataset()

    # A sanity check that the app itself works, before Lesson 9 runs it
    # against the whole dataset automatically.
    sample_question = EXAMPLES[0]["inputs"]["question"]
    print(f"\nSample run: {sample_question}")
    print(rag_answer(sample_question))


if __name__ == "__main__":
    main()
