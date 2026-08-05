"""
Lesson 12: Beginner checkpoint project - Prompted Story Generator.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/01_beginner/12_beginner_checkpoint_project/lesson.py

No new concepts here. This combines everything from Lessons 1-11 into
one small, real script: a story-opening generator that takes a fixed
genre and a batch of different character names, and produces a
consistently-styled one-paragraph opening for each one.
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model  # Lesson 11
from langchain_core.output_parsers import StrOutputParser  # Lesson 7
from langchain_core.prompts import (  # Lessons 3, 4, 5
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)
from langchain_core.runnables import RunnableLambda  # Lesson 8

load_dotenv()

# Lesson 11: provider chosen by string, not a provider-specific import.
model = init_chat_model("google_genai:gemini-3.5-flash-lite", temperature=0.9)
# Note from Lesson 10: this specific model ignores temperature (fixed
# sampling), so don't be surprised if outputs don't vary much between
# runs. The line above is still good practice, since a different model
# swapped in later (via the same init_chat_model string) might honor it.

# Lesson 5: a few worked examples, teaching the model our exact style,
# a two-sentence, atmospheric opening line, no dialogue.
examples = [
    {
        "character_name": "Mira",
        "opening": (
            "Mira had walked this corridor a hundred times, but tonight the "
            "shadows leaned the wrong way. Somewhere below, something knew "
            "her name."
        ),
    },
    {
        "character_name": "Dorian",
        "opening": (
            "Dorian counted the locks on the door twice before he trusted "
            "them. The letter on the table had arrived without a postmark."
        ),
    },
]

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "Character: {character_name}"),
        ("ai", "{opening}"),
    ]
)

few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

# Lesson 4: two blanks, {genre} and {character_name}.
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You write two-sentence, atmospheric story openings in the "
            "{genre} genre. No dialogue. Match the style of the examples.",
        ),
        few_shot_prompt,
        ("human", "Character: {character_name}"),
    ]
)

# Lesson 4: .partial() locks in "genre" for this whole run, since every
# story in this batch shares the same genre. Only "character_name"
# changes per story.
mystery_prompt = prompt.partial(genre="mystery")


# Lesson 8: a plain function, wrapped so it can sit inside the chain,
# adding a word count alongside the generated opening.
def add_word_count(opening: str) -> dict:
    return {"opening": opening, "word_count": len(opening.split())}


# Lesson 6: the full chain, template -> model -> parser -> our own step.
chain = mystery_prompt | model | StrOutputParser() | RunnableLambda(add_word_count)


def main() -> None:
    characters = ["Elena", "Marcus", "Priya"]

    # Lesson 9: .batch() runs all three characters concurrently, instead
    # of looping over .invoke() one at a time.
    results = chain.batch([{"character_name": name} for name in characters])

    for name, result in zip(characters, results):
        print(f"--- {name} ---")
        print(result["opening"])
        print(f"({result['word_count']} words)\n")


if __name__ == "__main__":
    main()
