"""
Lesson 6: chains, connecting steps together with `|`.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/01_beginner/06_chains_lcel/lesson.py

This reuses the same prompt template idea from Lesson 3, but instead of
calling prompt.invoke() and model.invoke() as two separate lines, we
connect them into one reusable pipeline with `|`.
"""

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a concise research assistant. Answer in at most two sentences.",
        ),
        ("human", "{question}"),
    ]
)

# `|` reads as "and then." This builds a chain: fill in the template,
# AND THEN send it to the model. Compare this one line to Lesson 3's two
# separate .invoke() calls, same two steps, now connected into one
# reusable pipeline.
chain = prompt | model


def main() -> None:
    # One .invoke() now does both steps: fill in {question}, send to the
    # model, hand back the model's response.
    response = chain.invoke({"question": "What is LangChain for?"})
    print(response.text)

    # Because `chain` is reusable, we can run it again with a different
    # question without rebuilding anything.
    response2 = chain.invoke({"question": "What is a prompt template?"})
    print(response2.text)


if __name__ == "__main__":
    main()
