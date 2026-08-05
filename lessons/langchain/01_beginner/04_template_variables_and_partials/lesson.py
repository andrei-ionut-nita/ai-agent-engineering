"""
Lesson 4: multiple blanks, and pre-filling some of them with .partial().

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/01_beginner/04_template_variables_and_partials/lesson.py
"""

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# Two blanks this time: {persona} and {question}. Lesson 3 only had one.
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are {persona}. Answer in at most two sentences."),
        ("human", "{question}"),
    ]
)


def main() -> None:
    # Filling in BOTH blanks at once, same idea as Lesson 3, just with
    # two dictionary keys instead of one.
    filled = prompt.invoke(
        {"persona": "a pirate", "question": "What is LangChain?"}
    )
    response = model.invoke(filled)
    print("Two blanks filled at once:")
    print(response.text)

    # .partial() pre-fills SOME of the blanks, ahead of time, producing a
    # new template that only has the remaining blank left. This matters
    # when one value is fixed for a whole session (like a chosen
    # persona) but the other changes on every call (like the question).
    pirate_prompt = prompt.partial(persona="a pirate")

    # From here on, pirate_prompt only needs {question}, "persona" is
    # already locked in. Notice we now only pass ONE key.
    filled_again = pirate_prompt.invoke({"question": "What is a prompt template?"})
    response_again = model.invoke(filled_again)
    print("\nUsing .partial(), only 'question' needed this time:")
    print(response_again.text)


if __name__ == "__main__":
    main()
