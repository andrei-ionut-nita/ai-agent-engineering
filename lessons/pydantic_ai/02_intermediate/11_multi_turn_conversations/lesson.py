"""
Lesson 11: multi-turn conversations with message_history.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/02_intermediate/11_multi_turn_conversations/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()

agent = Agent("google:gemini-3.5-flash-lite")


def main() -> None:
    conversation = [
        "My favorite color is teal. Remember that.",
        "What is my favorite color?",
        "What did I just ask you?",
    ]

    history = []
    for user_input in conversation:
        result = agent.run_sync(user_input, message_history=history)
        print(f"User: {user_input}")
        print(f"Agent: {result.output}\n")
        history = result.all_messages()

    print(f"Total messages accumulated: {len(history)}")


if __name__ == "__main__":
    main()
