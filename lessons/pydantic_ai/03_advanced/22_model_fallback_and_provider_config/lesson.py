"""
Lesson 22: model fallback and provider config.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/03_advanced/22_model_fallback_and_provider_config/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.fallback import FallbackModel

load_dotenv()

# The first model name is deliberately invalid, to demonstrate the
# automatic fallback to the second, real model.
fallback_model = FallbackModel(
    "google:gemini-9.9-does-not-exist",
    "google:gemini-3.5-flash-lite",
)

agent = Agent(fallback_model)


def main() -> None:
    result = agent.run_sync("Say hi in one word.")
    print("Output:", result.output)

    last_response = result.all_messages()[-1]
    print("Model that actually answered:", last_response.model_name)


if __name__ == "__main__":
    main()
