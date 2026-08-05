"""
Lesson 29: a retrieval node feeding a generation node.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/03_advanced/29_rag_node/lesson.py

Same spirit as the langchain course's lessons 27-29 (loading documents,
retrieving relevant chunks, generating an answer grounded in them), kept
minimal here: a few hardcoded documents and plain keyword scoring
instead of a vector store dependency, so the lesson stays self-contained.
One node retrieves, a second node generates from what was retrieved.
"""

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# A tiny local "document store": no vector database, no embeddings API
# call, just enough text to prove the retrieval step actually matters.
DOCUMENTS = [
    "The office recycling bins are collected every Tuesday and Friday morning.",
    "Employees get 20 days of paid vacation per year, accrued monthly.",
    "The VPN client must be updated to version 4.2 before October, older versions stop working.",
    "Parking permits for the garage are issued by building security on the ground floor.",
    "The 401k match is 4% of salary, fully vested after two years.",
]


class State(TypedDict):
    question: str
    retrieved: list[str]
    answer: str


def retrieve(state: State) -> dict:
    # Deliberately simple: score each document by how many of the
    # question's words it contains, keep the top 2. No embeddings, no
    # external service, this is enough to demonstrate "retrieval changes
    # what the model can answer" without adding a new dependency.
    question_words = set(state["question"].lower().split())
    scored = sorted(
        DOCUMENTS,
        key=lambda doc: len(question_words & set(doc.lower().split())),
        reverse=True,
    )
    return {"retrieved": scored[:2]}


def generate(state: State) -> dict:
    context = "\n".join(f"- {doc}" for doc in state["retrieved"])
    prompt = (
        "Answer the question using ONLY the context below. If the context "
        "doesn't contain the answer, say you don't know.\n\n"
        f"Context:\n{context}\n\nQuestion: {state['question']}"
    )
    response = model.invoke(prompt)
    return {"answer": response.text}


builder = StateGraph(State)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_edge(START, "retrieve")
# The generation node never sees the raw DOCUMENTS list, only whatever
# the retrieval node decided was relevant, same separation of concerns
# as any two-node pipeline since Lesson 3.
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)
app = builder.compile()


def main() -> None:
    for question in [
        "How much vacation do employees get?",
        "When are recycling bins collected?",
        "What is the office WiFi password?",  # not in any document, on purpose
    ]:
        result = app.invoke({"question": question, "retrieved": [], "answer": ""})
        print(f"Q: {question}")
        print(f"  Retrieved: {result['retrieved']}")
        print(f"  A: {result['answer']}\n")


if __name__ == "__main__":
    main()
