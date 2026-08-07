"""
Lesson 3: send one prompt to a local model and print what it says back.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/01_beginner/03_first_generate_call/lesson.py

This is the local-model version of langchain Lesson 1: one prompt in,
one answer out, no conversation history, no tools, nothing else yet.
"""

import ollama

# No API key, no load_dotenv(): the request goes to http://localhost:11434,
# not to a company's servers, so there's nothing to authenticate.
response = ollama.generate(
    model="llama3.2",
    prompt="In one sentence, what is Python used for?",
)


def main() -> None:
    # response is a GenerateResponse object, similar in spirit to LangChain's
    # AIMessage: the written answer plus metadata about the call.
    print(response.response)

    # eval_count is roughly how many tokens (word-pieces) the model
    # generated; prompt_eval_count is how many it had to read from your
    # prompt first. Printed here so you can see this is real metadata,
    # not just a wrapped string.
    print(f"\n(generated {response.eval_count} tokens, read {response.prompt_eval_count} tokens of prompt)")


if __name__ == "__main__":
    main()
