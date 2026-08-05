# Lesson 22: Intermediate Checkpoint - CLI Assistant with a Tool and Memory

## What this is

No new concepts. This is a checkpoint: a small, real CLI assistant built
entirely out of ideas from Lessons 13 through 21, combined into one
thing, still without `create_agent` (that's Lesson 23, the start of
Advanced). If you can read `lesson.py` and understand why every piece is
there, you've mastered the Intermediate tier.

## What it does

A command-line chat loop with two tools (a calculator and a word
counter), manual conversation memory, graceful handling of failing tool
calls, automatic retries on transient API errors, and an on-demand
structured summary of the conversation so far.

## Where each piece came from

```python
@tool
def calculator(...): ...
@tool
def word_counter(...): ...
TOOLS_BY_NAME = {"calculator": calculator, "word_counter": word_counter}
```
Lessons 13-15: two distinct tools, looked up by name once the model
picks one.

```python
model_with_tools = model.bind_tools([calculator, word_counter])
```
Lesson 14/15: both tools bound to the model at once.

```python
try:
    result = chosen_tool.invoke(call["args"])
except Exception as error:
    result = f"Error: {error}"
```
Lesson 16: a failing tool call (say, asking the calculator to divide by
zero) gets reported back to the model as a `ToolMessage`, instead of
crashing the whole CLI session.

```python
history: list = []
...
history.append(HumanMessage(user_input))
...
history.append(ai_message)
```
Lesson 17: `history` is the conversation's actual memory, resent in full
to the model on every turn, exactly as introduced back then.

```python
class ConversationSummary(BaseModel):
    topics_discussed: list[str] = ...
    overall_tone: str = ...

structured_model = model.with_structured_output(ConversationSummary)
```
Lesson 18. Typing `"summary"` triggers a separate call asking for a
real, typed `ConversationSummary` object, not free text to parse.

```python
def invoke_with_retry(runnable, payload, max_attempts: int = 3):
    ...
```
Lesson 21's manual retry-with-backoff pattern, wrapped around every real
API call in this script (both the tool-using calls and the summary
call).

## Why `tool_calls_made` is computed in Python, not asked of the model

```python
tool_calls_made = sum(len(m.tool_calls) for m in history if isinstance(m, AIMessage))
```

Notice this count is computed directly from `history`, in plain Python,
rather than being one of the fields we ask `ConversationSummary` to fill
in. The model has no reliable way to count exactly how many tool calls
happened purely by reading a text transcript, and Lesson 18 already
established the difference between things a model can *reasonably
judge* (like the overall tone of a conversation) versus things that need
to be *exactly correct* (a count). Counting is something code should
do; judging tone and topic is something worth asking a model for.

## Running it

```bash
uv run python lessons/langchain/02_intermediate/22_intermediate_checkpoint_project/lesson.py
```

Try a conversation like:

```
You: What is 84 times 12?
Assistant: 84 times 12 is 1,008.

You: How many words are in 'the quick brown fox'?
Assistant: There are 4 words in "the quick brown fox".

You: summary
--- Summary ---
Topics: multiplication, word count
Tool calls made: 2
Tone: informative
```

## Try this yourself

Without looking anything up:

- Ask a question that would make the calculator divide by zero, and
  confirm the assistant explains the problem instead of crashing.
- Add a third tool of your own (anything, a text reverser, a
  temperature converter) and confirm the model correctly chooses between
  all three based on the question asked.

If you can make these changes confidently, you're ready for the
Advanced tier, starting at Lesson 23.
