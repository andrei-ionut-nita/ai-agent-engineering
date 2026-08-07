"""
Lesson 16: baking a system prompt into a named, reusable model.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/02_intermediate/16_custom_models_with_modelfile/lesson.py

This creates a new local model, "pirate-pete", built on top of
llama3.2, and deletes it again at the end so it doesn't stick around
on your disk after the lesson.
"""

import ollama

CUSTOM_MODEL_NAME = "pirate-pete"
SYSTEM_PROMPT = (
    "You are Pirate Pete, a pirate-themed coding assistant. "
    "Always answer in pirate speak, but keep technical accuracy intact."
)


def main() -> None:
    # ollama.create() is the Python equivalent of writing a Modelfile and
    # running `ollama create pirate-pete -f Modelfile` on the CLI. The
    # Modelfile itself is just a small text format:
    #
    #     FROM llama3.2
    #     SYSTEM You are Pirate Pete, a pirate-themed coding assistant. ...
    #     PARAMETER temperature 0.7
    #
    # "FROM" picks the base model, "SYSTEM" bakes in a fixed system
    # prompt, "PARAMETER" bakes in default options (Lesson 6). Python
    # code passes the same three pieces as keyword arguments instead.
    print(f"Creating {CUSTOM_MODEL_NAME}, built on llama3.2...")
    for _ in ollama.create(
        model=CUSTOM_MODEL_NAME,
        from_="llama3.2",
        system=SYSTEM_PROMPT,
        parameters={"temperature": 0.7},
    ):
        pass  # create() streams progress updates; we don't need them here.

    # Once created, the custom model is called exactly like any other,
    # no system message needed in the call itself, it's already baked in.
    response = ollama.chat(
        model=CUSTOM_MODEL_NAME,
        messages=[{"role": "user", "content": "What is a variable in programming?"}],
    )
    print(f"\n{CUSTOM_MODEL_NAME} answering with no system message in this call:")
    print(response.message.content)

    # Confirm the system prompt really is stored on the model itself, not
    # something this script re-sent. ollama.show() returns the model's
    # full generated Modelfile as text; the SYSTEM line inside it is
    # where the prompt actually lives.
    info = ollama.show(CUSTOM_MODEL_NAME)
    system_line = next(line for line in info.modelfile.splitlines() if line.startswith("SYSTEM"))
    print(f"\nBaked-in system prompt, from ollama.show(): {system_line}")

    # Clean up: this was created just for this lesson, remove it so it
    # doesn't take up permanent disk space, same pattern as Lesson 7.
    ollama.delete(CUSTOM_MODEL_NAME)
    print(f"\nDeleted {CUSTOM_MODEL_NAME}.")


if __name__ == "__main__":
    main()
