"""
Lesson 13: pushing a prompt to the Prompt Hub, then pulling it back.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langsmith/02_intermediate/13_prompt_hub/lesson.py
"""

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
client = Client()

PROMPT_NAME = "langsmith-course-rag-prompt"

DOCS = {
    "langchain": "LangChain is a framework for building LLM applications with a shared interface across model providers.",
    "langgraph": "LangGraph is a library for building stateful, graph-based agents on top of LangChain.",
    "langsmith": "LangSmith is a platform for tracing, evaluating, and monitoring LLM applications in development and production.",
}


def retrieve(question: str) -> list[str]:
    matches = [text for key, text in DOCS.items() if key in question.lower()]
    return matches or list(DOCS.values())


def publish_prompt() -> None:
    # A prompt is just a ChatPromptTemplate, exactly like the ones from
    # the langchain course, but pushed to LangSmith's Prompt Hub instead
    # of only living in this Python file.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer using only the given context, in one short sentence.",
            ),
            ("human", "Context:\n{context}\n\nQuestion: {question}"),
        ]
    )
    # push_prompt stores (or updates) the prompt under this name in the
    # hub, versioned, viewable, and editable from the LangSmith UI, not
    # just from this file.
    client.push_prompt(PROMPT_NAME, object=prompt)
    print(f"Pushed prompt '{PROMPT_NAME}' to the hub.")


def main() -> None:
    publish_prompt()

    # pull_prompt fetches the current version of a named prompt from
    # the hub. Anyone, or anything, with access to this LangSmith
    # workspace can now use this exact prompt without copying its text.
    prompt = client.pull_prompt(PROMPT_NAME)

    question = "What is LangGraph used for?"
    context = "\n".join(retrieve(question))
    chain = prompt | model
    response = chain.invoke({"context": context, "question": question})
    print(response.text)


if __name__ == "__main__":
    main()
