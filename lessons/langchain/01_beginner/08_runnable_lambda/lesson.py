"""
Lesson 8: RunnableLambda, wrapping your own function into a chain.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/01_beginner/08_runnable_lambda/lesson.py
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Answer in at most one sentence."),
        ("human", "{question}"),
    ]
)


# A plain Python function, nothing LangChain-specific about it. It takes
# whatever the raw user typed and cleans it up before it ever reaches
# the template.
def clean_question(raw_question: str) -> dict:
    cleaned = raw_question.strip()
    if not cleaned.endswith("?"):
        cleaned += "?"
    # The prompt template expects a dict with a "question" key, so this
    # function has to hand back exactly that shape.
    return {"question": cleaned}


# A second plain function, this one runs AFTER the model's answer comes
# back as plain text, adding a word count alongside it.
def add_word_count(answer: str) -> dict:
    return {"answer": answer, "word_count": len(answer.split())}


# RunnableLambda wraps a plain function so it can sit inside a chain
# built with `|`, same interface as every other step: it gets an
# .invoke() method, matching prompt, model, and parser.
clean_step = RunnableLambda(clean_question)
count_step = RunnableLambda(add_word_count)

chain = clean_step | prompt | model | StrOutputParser() | count_step


def main() -> None:
    # We can call clean_step on its own, same .invoke() as everything
    # else, to see exactly what it does in isolation.
    print("clean_step alone:", clean_step.invoke("  what is langchain  "))

    # Now the full chain: raw, messy input goes in one end, a dict with
    # both the answer AND a word count comes out the other end. Neither
    # "cleaning input" nor "counting words" is a built-in LangChain
    # feature, both are just our own functions, wired in.
    result = chain.invoke("  what is langchain  ")
    print("\nFull chain result:", result)


if __name__ == "__main__":
    main()
