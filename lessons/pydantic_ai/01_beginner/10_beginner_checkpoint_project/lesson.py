"""
Lesson 10 (Checkpoint): a validated research-notes assistant.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/01_beginner/10_beginner_checkpoint_project/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

from dataclasses import dataclass, field

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent, ModelRetry, RunContext

load_dotenv()

# A tiny fake knowledge base, standing in for a real search API so this
# lesson runs with nothing but a Gemini key.
FAKE_KNOWLEDGE_BASE = {
    "pydantic ai": (
        "Pydantic AI is a type-safe agent framework from the Pydantic "
        "team. Agents declare deps_type and output_type; outputs are "
        "validated Pydantic models, not raw strings."
    ),
}


class ResearchNote(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    confidence: float


@dataclass
class ResearchDeps:
    notes: dict[str, ResearchNote] = field(default_factory=dict)


agent = Agent(
    "google:gemini-3.5-flash-lite",
    deps_type=ResearchDeps,
    output_type=ResearchNote,
    system_prompt=(
        "You are a research assistant. For the given topic: call "
        "fake_search to gather evidence, call save_note to persist your "
        "findings, then produce a final ResearchNote with at least two "
        "key_points and a confidence between 0.0 and 1.0."
    ),
)


@agent.tool_plain
def fake_search(topic: str) -> str:
    """Search a small internal knowledge base for a topic.

    Args:
        topic: The topic to search for, lowercase.
    """
    return FAKE_KNOWLEDGE_BASE.get(
        topic.lower(), f"No entries found for '{topic}'."
    )


@agent.tool
def save_note(ctx: RunContext[ResearchDeps], note: ResearchNote) -> str:
    """Save a finished research note.

    Args:
        note: The research note to persist.
    """
    ctx.deps.notes[note.title] = note
    return f"Saved note '{note.title}'."


@agent.output_validator
def validate_note(ctx: RunContext[ResearchDeps], output: ResearchNote) -> ResearchNote:
    if not output.key_points:
        raise ModelRetry("key_points must not be empty. Try again.")
    if not (0.0 <= output.confidence <= 1.0):
        raise ModelRetry("confidence must be between 0.0 and 1.0. Try again.")
    return output


def main() -> None:
    deps = ResearchDeps()
    result = agent.run_sync("Research the topic 'Pydantic AI'.", deps=deps)

    note = result.output
    print("Title:", note.title)
    print("Summary:", note.summary)
    print("Key points:")
    for point in note.key_points:
        print("  -", point)
    print("Confidence:", note.confidence)
    print("\nNotes saved during the run:", list(deps.notes.keys()))


if __name__ == "__main__":
    main()
