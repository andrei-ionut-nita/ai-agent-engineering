"""
Lesson 11: init_chat_model, choosing a provider with a string.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/01_beginner/11_provider_agnostic_models/lesson.py
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def main() -> None:
    # This is what every lesson so far has done: import a specific
    # class for a specific provider, and construct it directly.
    direct_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    print("Direct import:", type(direct_model).__name__)
    print(direct_model.invoke("Say hello in one word.").text)

    # init_chat_model does the same thing, but you never import a
    # provider-specific class. The provider is chosen entirely from the
    # string, "google_genai:gemini-3.5-flash-lite" means "use the Google
    # Gemini integration, with this specific model."
    agnostic_model = init_chat_model("google_genai:gemini-3.5-flash-lite")
    print("\ninit_chat_model:", type(agnostic_model).__name__)
    print(agnostic_model.invoke("Say hello in one word.").text)

    # Notice: init_chat_model still returned the exact same class,
    # ChatGoogleGenerativeAI, underneath. It didn't create some new kind
    # of object, it just picked which class to build FOR you, based on
    # reading the "google_genai:" prefix in the string.
    print(
        "\nSame underlying class?",
        type(direct_model) is type(agnostic_model),
    )


if __name__ == "__main__":
    main()
