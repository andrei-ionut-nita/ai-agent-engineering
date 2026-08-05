"""
Lesson 5: few-shot prompting, showing the model examples instead of
just describing what you want.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/01_beginner/05_few_shot_prompting/lesson.py
"""

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# Each example is one (input, output) pair, showing the exact style we
# want: turning a sentence into a single all-caps keyword.
examples = [
    {"input": "The cat is sleeping on the warm windowsill.", "output": "SLEEPING"},
    {"input": "She sprinted across the finish line first.", "output": "RUNNING"},
    {"input": "He is reading a mystery novel by the fire.", "output": "READING"},
]

# This template formats ONE example into a human/ai message pair. Notice
# its blanks, {input} and {output}, match the keys used in `examples`
# above.
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

# FewShotChatMessagePromptTemplate expands the whole `examples` list
# through `example_prompt`, producing several human/ai message pairs in
# a row, one per example, all before the real question ever appears.
few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

# The final template: a system message, then all the worked examples,
# then the real, new question.
final_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Summarize the main action in the sentence with one word."),
        few_shot_prompt,
        ("human", "{input}"),
    ]
)


def main() -> None:
    filled = final_prompt.invoke(
        {"input": "The children were laughing loudly in the playground."}
    )

    print("Full conversation sent to the model:")
    for message in filled.to_messages():
        print(f"  [{message.type}] {message.content}")

    response = model.invoke(filled)
    print("\nModel's answer:", response.text)


if __name__ == "__main__":
    main()
