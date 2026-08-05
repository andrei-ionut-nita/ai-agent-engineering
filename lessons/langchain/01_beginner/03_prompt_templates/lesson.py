"""
Lesson 3: prompt templates, filling in blanks before sending a message.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/01_beginner/03_prompt_templates/lesson.py

This lesson deliberately stops short of chaining steps together with `|`,
that's Lesson 6. Here we call the template and the model as two separate,
visible steps, so it's clear what each one does on its own.
"""

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# A template is a message structure with a blank to fill in later.
# "system" sets standing instructions for the whole conversation.
# "human" is the user's message, with a placeholder named {question}.
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a concise research assistant. Answer in at most two sentences.",
        ),
        ("human", "{question}"),
    ]
)


def main() -> None:
    # Step 1: fill in the template's blank. The dictionary's key
    # ("question") must match the {question} placeholder's name exactly.
    filled_prompt = prompt.invoke({"question": "What is LangChain for?"})

    # filled_prompt is now a real, ready-to-send list of messages, you can
    # print it to see the system + human messages with the blank filled.
    print("Filled-in messages:")
    for message in filled_prompt.to_messages():
        print(f"  [{message.type}] {message.content}")

    # Step 2: send the filled-in messages to the model, same .invoke()
    # you've used since Lesson 1, just receiving messages instead of a
    # single string this time.
    response = model.invoke(filled_prompt)
    print("\nModel's answer:")
    print(response.text)


if __name__ == "__main__":
    main()
