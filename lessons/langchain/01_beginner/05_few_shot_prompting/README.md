# Lesson 5: Few-shot prompting, teaching by example

## The limits of describing what you want

Every template so far has told the AI what to do in words: "answer in
two sentences," "you are a pirate." That works for behavior, but it's
clumsy for describing an exact *format*, especially a format that's
easier to show than to describe. Try writing instructions in plain
English for "summarize a sentence as a single all-caps word matching the
main action", and you'll notice it's fiddly to get exactly right. It's
much easier to just show a few examples and let the pattern speak for
itself.

That's **few-shot prompting**: instead of (or in addition to)
describing the task, you show the model a handful of correctly-done
examples, then give it a new, real input and let it continue the
pattern.

## One example, formatted

```python
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)
```

This is a small template (same idea as every template since Lesson 3)
that turns one `{"input": ..., "output": ...}` pair into a fake
human/ai exchange, a pretend little snippet of conversation where the
human asked something and the ai answered exactly the way we want.

## Many examples, expanded automatically

```python
examples = [
    {"input": "The cat is sleeping on the warm windowsill.", "output": "SLEEPING"},
    {"input": "She sprinted across the finish line first.", "output": "RUNNING"},
    {"input": "He is reading a mystery novel by the fire.", "output": "READING"},
]

few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)
```

`FewShotChatMessagePromptTemplate` runs every dictionary in `examples`
through `example_prompt`, producing one fake human/ai exchange per
example, all strung together in order. Three examples in, three
human/ai pairs come out.

## Assembling the final template

```python
final_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Summarize the main action in the sentence with one word."),
        few_shot_prompt,
        ("human", "{input}"),
    ]
)
```

Notice `few_shot_prompt` is dropped directly into the messages list,
right alongside plain `("system", ...)` and `("human", ...)` tuples.
`ChatPromptTemplate` is fine mixing a block of expanded examples in with
regular messages. The very last entry, `("human", "{input}")`, is the
real question, still just a blank, waiting to be filled with something
new.

## What the model actually receives

Run the lesson and look at the printed conversation:

```
[system] Summarize the main action in the sentence with one word.
[human] The cat is sleeping on the warm windowsill.
[ai] SLEEPING
[human] She sprinted across the finish line first.
[ai] RUNNING
[human] He is reading a mystery novel by the fire.
[ai] READING
[human] The children were laughing loudly in the playground.
```

The model reads this the same way it read the memory example back in
Lesson 2: as one long conversation. It sees three rounds of "human asks,
ai answers in a specific style," then a fourth human message with no
answer yet. The most natural continuation, given everything it just
read, is to answer in that same style: `LAUGHING`. Nobody told it
"respond in all caps with one word" in plain English, it inferred the
format purely from the pattern.

## Running it

```bash
uv run python lessons/langchain/01_beginner/05_few_shot_prompting/lesson.py
```

## Try this yourself

Add a fourth example to `examples` with a different, weirder format
(say, output wrapped in brackets, like `[SLEEPING]`), rerun the lesson,
and see the new sentence get answered in that format too, purely from
pattern-following.

## Checkpoint

- **few-shot prompting**: showing the model worked examples of the task,
  instead of (or alongside) describing it in words.
- **`FewShotChatMessagePromptTemplate`**: expands a list of
  input/output examples into repeated human/ai message pairs.
- **why it works**: the model treats the whole thing as one
  conversation, and continues the pattern it just saw, the same
  mechanism from Lesson 2's "memory preview."

If anything here still feels unclear, ask before moving to Lesson 6.
