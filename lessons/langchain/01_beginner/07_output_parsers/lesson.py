"""
Lesson 7: output parsers, reshaping the model's reply automatically.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/01_beginner/07_output_parsers/lesson.py
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a concise research assistant."),
        ("human", "{question}"),
    ]
)


def main() -> None:
    # Without a parser, chain.invoke() hands back a whole AIMessage
    # object, like every response since Lesson 1. You still have to
    # reach for .text yourself.
    plain_chain = prompt | model
    plain_result = plain_chain.invoke({"question": "What is LangChain in one sentence?"})
    print("No parser, result type:", type(plain_result).__name__)
    print("Still need .text:", plain_result.text)

    # StrOutputParser adds one more step: it automatically reaches into
    # the AIMessage and pulls out just the text, same idea as .text, now
    # baked into the chain itself.
    str_chain = prompt | model | StrOutputParser()
    str_result = str_chain.invoke({"question": "What is LangChain in one sentence?"})
    print("\nWith StrOutputParser, is it plain text now?", isinstance(str_result, str))
    print("Already plain text:", str_result)

    # JsonOutputParser expects the model's reply to BE a JSON string, and
    # parses it into a real Python dict automatically. Notice we have to
    # ask the model, in the prompt, to actually respond in JSON, the
    # parser only handles turning that JSON text into a dict, it can't
    # make the model produce JSON on its own.
    json_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Respond ONLY with JSON in the form "
                '{{"answer": "...", "one_word_topic": "..."}}, nothing else.',
            ),
            ("human", "{question}"),
        ]
    )
    json_chain = json_prompt | model | JsonOutputParser()
    json_result = json_chain.invoke({"question": "What is LangChain in one sentence?"})
    print("\nWith JsonOutputParser, result type:", type(json_result).__name__)
    print("Parsed dict:", json_result)
    print("Accessing a field directly:", json_result["one_word_topic"])


if __name__ == "__main__":
    main()
