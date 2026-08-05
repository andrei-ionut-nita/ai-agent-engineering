"""
Lesson 10: model parameters, controlling determinism and length.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/01_beginner/10_model_parameters/lesson.py

Fair warning: running this may print a UserWarning from
langchain_google_genai. That warning IS the lesson, read README.md's
"An honest surprise" section before assuming something is broken.
"""

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

question = "Give me a one-word, made-up name for a pet robot."


def main() -> None:
    # temperature controls how "random" the model's word choices are, in
    # theory. Low temperature (close to 0): pick the most likely next
    # word almost every time, answers tend to repeat across separate
    # calls. High temperature: more willing to pick less-likely words,
    # answers tend to vary more.
    #
    # "gemini-3.5-flash-lite" is a small, fast model, and it turns out it
    # uses FIXED sampling settings internally, it ignores temperature
    # entirely (LangChain will print a UserWarning saying exactly this).
    # We're asking anyway, on purpose, so you see that warning yourself
    # rather than just being told about it.
    steady_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0)
    creative_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=1.0)

    print("temperature=0, asked 3 times:")
    for _ in range(3):
        print(" ", steady_model.invoke(question).text)

    print("\ntemperature=1.0, asked 3 times:")
    for _ in range(3):
        print(" ", creative_model.invoke(question).text)

    print(
        "\n(If both lists above look similarly varied, and you saw a "
        "UserWarning about 'fixed sampling defaults', that's expected, "
        "see README.md.)"
    )

    # max_output_tokens caps how long a reply is allowed to be. A "token"
    # is roughly a word-piece, not exactly a word or a character. Setting
    # this very low can cut a reply off mid-sentence. Unlike temperature,
    # this one actually works on this model.
    short_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", max_output_tokens=10)
    long_answer = short_model.invoke("Explain what LangChain is.")
    print("\nmax_output_tokens=10, cut off mid-sentence:")
    print(" ", long_answer.text)


if __name__ == "__main__":
    main()
