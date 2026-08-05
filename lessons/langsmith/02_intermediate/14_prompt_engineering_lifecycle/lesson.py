"""
Lesson 14: the prompt engineering lifecycle, iterate, re-run, compare.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/02_intermediate/14_prompt_engineering_lifecycle/lesson.py
"""

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client, traceable
from langsmith.evaluation import evaluate

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
client = Client()

PROMPT_NAME = "langsmith-course-rag-prompt"
DATASET_NAME = "langsmith-course-rag-qa"

DOCS = {
    "langchain": "LangChain is a framework for building LLM applications with a shared interface across model providers.",
    "langgraph": "LangGraph is a library for building stateful, graph-based agents on top of LangChain.",
    "langsmith": "LangSmith is a platform for tracing, evaluating, and monitoring LLM applications in development and production.",
}


@traceable(run_type="retriever")
def retrieve(question: str) -> list[str]:
    matches = [text for key, text in DOCS.items() if key in question.lower()]
    return matches or list(DOCS.values())


def keyword_overlap(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    reference_words = set(reference_outputs["answer"].lower().split())
    answer_words = set(outputs["answer"].lower().split())
    overlap = reference_words & answer_words
    score = len(overlap) / len(reference_words) if reference_words else 0.0
    return {"key": "keyword_overlap", "score": round(score, 2)}


def make_target(prompt: ChatPromptTemplate):
    # Building target() from whatever prompt is currently pulled means
    # the same evaluation code runs unchanged, only the prompt differs,
    # between the "before" and "after" experiments below.
    chain = prompt | model

    def target(inputs: dict) -> dict:
        context = "\n".join(retrieve(inputs["question"]))
        response = chain.invoke({"context": context, "question": inputs["question"]})
        return {"answer": response.text}

    return target


def main() -> None:
    # Step 1: run an experiment against a deliberately naive first-draft
    # prompt, the mistake every first RAG prompt tends to make: it never
    # actually references {context}, so the model answers from whatever
    # it already knows, not from what retrieve() found. make_target()
    # still builds context and passes it into the invoke() call, but a
    # prompt with no {context} placeholder simply never uses it, the
    # same as if a real app forgot to wire retrieval into its prompt.
    naive_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Answer in one short sentence."),
            ("human", "Question: {question}"),
        ]
    )
    baseline = evaluate(
        make_target(naive_prompt),
        data=DATASET_NAME,
        evaluators=[keyword_overlap],
        experiment_prefix="rag-lifecycle-v1",
    )
    print(f"v1 experiment (no context in the prompt): {baseline.experiment_name}")

    # Step 2: the fix, ground the answer in the retrieved context, the
    # same prompt already pushed to the hub in Lesson 13. Pushing it
    # again here is what makes this lesson runnable on its own, without
    # depending on Lesson 13 having run first.
    grounded_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer using only the given context, in one short sentence.",
            ),
            ("human", "Context:\n{context}\n\nQuestion: {question}"),
        ]
    )
    client.push_prompt(PROMPT_NAME, object=grounded_prompt)

    # Step 3: pull the new version back (proving it's really the hub's
    # version being used, not the local variable) and re-run the exact
    # same evaluation.
    v2_prompt = client.pull_prompt(PROMPT_NAME)
    v2 = evaluate(
        make_target(v2_prompt),
        data=DATASET_NAME,
        evaluators=[keyword_overlap],
        experiment_prefix="rag-lifecycle-v2",
    )
    print(f"v2 experiment (context grounded): {v2.experiment_name}")
    print("Compare the two experiments' keyword_overlap scores in the UI, "
          "v2 should score noticeably higher.")


if __name__ == "__main__":
    main()
