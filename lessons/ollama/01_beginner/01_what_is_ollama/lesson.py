"""
Lesson 1: what is Ollama, and is it actually installed and working.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/01_beginner/01_what_is_ollama/lesson.py

Every other course in this repo sends your request over the internet to
Google's servers and gets Gemini's reply back. This one is different:
Ollama runs the model on your own machine, and talks to it over a local
HTTP server instead of the public internet.
"""

import ollama

CLOUD_VS_LOCAL = {
    "Where the model runs": "Google's servers (cloud) vs your machine (local)",
    "Network required": "Yes, every call vs no, after the model is downloaded",
    "Cost": "Free tier, then per-token vs free, limited only by your hardware",
    "Privacy": "Your prompts leave your machine vs your prompts never leave it",
    "Quality ceiling": "Very high (huge models) vs lower (bounded by your RAM/GPU)",
    "Speed": "Depends on network + provider load vs depends on your hardware",
}


def main() -> None:
    print("Cloud (Gemini, every other course) vs local (Ollama, this course):")
    for aspect, comparison in CLOUD_VS_LOCAL.items():
        print(f"  {aspect}: {comparison}")

    # ollama.list() asks the local Ollama server (http://localhost:11434 by
    # default) what models have already been downloaded to this machine.
    # It's a real network call, just to localhost instead of the internet,
    # which is why it fails loudly if the Ollama application isn't running.
    print("\nModels already pulled on this machine:")
    try:
        response = ollama.list()
    except ConnectionError as exc:
        raise SystemExit(
            "Could not reach the local Ollama server. Is the Ollama "
            "application installed and running? See this project's root "
            "README, Prerequisites section, or run `ollama serve` in "
            "another terminal."
        ) from exc

    if not response.models:
        raise SystemExit(
            "Ollama is running, but no models are pulled yet. Run "
            "`ollama pull llama3.2` (see this course's README) before "
            "continuing to Lesson 2."
        )

    for model in response.models:
        size_gb = model.size / 1_000_000_000
        print(f"  {model.model} ({size_gb:.1f} GB, {model.details.parameter_size} params)")


if __name__ == "__main__":
    main()
