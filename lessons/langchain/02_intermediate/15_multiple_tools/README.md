# Lesson 15: Multiple tools, letting the model choose

## Where we left off

Lesson 14 bound exactly one tool, the calculator, so there was never any
real choice involved, if the model wanted a tool at all, it could only
mean the calculator. This lesson binds two tools with clearly different
purposes, and asks three different kinds of questions to see the model
actually choose between them.

## A second, unrelated tool

```python
@tool
def word_counter(text: str) -> str:
    """Count how many words are in a piece of text."""
    return str(len(text.split()))
```

Same `@tool` pattern from Lesson 13, a completely different job:
counting words instead of doing arithmetic. The two tools don't overlap
at all, which matters for this lesson, we want it to be obvious which
one (if either) a given question should trigger.

## Binding both at once

```python
model_with_tools = model.bind_tools([calculator, word_counter])
```

Same `bind_tools` from Lesson 14, just handed a list of two tools
instead of one. The model now sees descriptions of both, and has to
decide, per question, which one (if any) actually applies.

## Looking up which tool was actually requested

```python
tools_by_name = {"calculator": calculator, "word_counter": word_counter}
for call in ai_message.tool_calls:
    chosen_tool = tools_by_name[call["name"]]
    result = chosen_tool.invoke(call["args"])
```

In Lesson 14, there was only one tool, so we always knew which function
to run. Now that there are two, each `tool_calls` entry includes a
`"name"` field telling us which one the model actually picked, and we
look up the matching real function by that name before running it. This
`tools_by_name` dictionary pattern is how you'd generalize this to any
number of tools, not just two.

## Three questions, three outcomes

```python
ask("What is 84 times 17?")
ask("How many words are in the sentence: 'The quick brown fox jumps'?")
ask("What is the capital of France?")
```

Run the lesson and you'll see three different behaviors:

1. The math question triggers `calculator`.
2. The word-counting question triggers `word_counter`.
3. The capital-of-France question triggers **neither**, the model just
   answers directly, exactly like every plain question since Lesson 1.

That third case matters as much as the first two. Binding tools to a
model doesn't force it to use one, it gives it the *option*. A
well-behaved model only reaches for a tool when the question actually
calls for it, answering directly the rest of the time.

## Running it

```bash
uv run python lessons/langchain/02_intermediate/15_multiple_tools/lesson.py
```

## Checkpoint

- **multiple tools**: `bind_tools` accepts a list of any size, the model
  picks which one (if any) fits a given question.
- **`call["name"]`**: tells you which specific tool the model requested,
  needed to look up the right function once more than one is available.
- **choosing no tool**: binding tools doesn't force their use, the model
  can still answer directly when no tool is relevant.

If anything here still feels unclear, ask before moving to Lesson 16.
