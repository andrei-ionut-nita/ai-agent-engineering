# Lesson 14: Handing a tool to a model

## Where we left off

Lesson 13 built a `calculator` tool and called it directly, no AI
involved. This lesson connects that same tool to a model, and walks
through what actually happens when an AI uses a tool.

## Connecting the tool to the model

```python
model_with_tools = model.bind_tools([calculator])
```

`bind_tools` does not give the model the power to run Python. The model
can never execute code, it only ever produces text. What `bind_tools`
does is describe the tool (its name, description, and argument schema,
exactly what Lesson 13 printed) to the model, so that when the model
wants to use it, it can output a special structured message meaning
"please run `calculator` with this input", instead of guessing an answer
in plain words.

## The three rounds of conversation

Talking to a model with tools isn't one message and one reply, it's a
back-and-forth, usually three steps.

**Round 1: ask the question.**

```python
ai_message = model_with_tools.invoke(messages)
```

We send: *"What is 847293 multiplied by 3821?"* The model recognizes it
needs exact arithmetic, and instead of answering in words, it replies
with a request: *"call `calculator` with expression = '847293 * 3821'"*.
This request lives in `ai_message.tool_calls`, a list, since the model
could ask for more than one tool call at once.

**Round 2: we run the tool ourselves, and report back.**

```python
for call in ai_message.tool_calls:
    result = calculator.invoke(call["args"])
    messages.append(ToolMessage(content=result, tool_call_id=call["id"]))
```

The model asked, but it cannot press the button itself, our program has
to actually run `calculator.invoke(...)`. This is the important idea to
hold onto: **the AI decides, but your code executes.** The AI never
directly touches your computer, your files, or the internet. It only
produces a request; your program chooses whether to honor it, and is the
one that actually does it.

`ToolMessage` wraps the result and gets added to the conversation.
`tool_call_id` is like a receipt number, it tells the model "this result
answers the specific request you made with this ID" (useful when there
are multiple tool calls at once, so results don't get mixed up).

**Round 3: let the model turn the number into a sentence.**

```python
final_response = model_with_tools.invoke(messages)
```

We send the *entire conversation so far*: the original question, the
model's own tool request, and the tool's result. The model reads all of
that and writes a normal, human-sounding final answer, using the exact
number the calculator produced instead of guessing.

## Why does `messages` keep growing?

Notice `messages` starts as one item and ends up with four: the
question, the AI's tool request, our tool result, and the final answer.
Each `.invoke()` call doesn't remember anything on its own, the model has
no memory between calls. Every time we call `.invoke()`, we hand it the
*entire* conversation so far, or it won't know what already happened.
This will matter a lot in Lesson 17.

## Running it

```bash
uv run python lessons/langchain/02_intermediate/14_tool_calling/lesson.py
```

Try changing the numbers in the question to something bigger. You should
still get an exact answer, because the calculator, not the model, is
doing the actual multiplication.

## Checkpoint

- **`bind_tools`**: attaches a list of available tools to a model, so its
  replies can include requests to use them.
- **tool call**: a structured request from the model, "please run this
  tool with these arguments", found in `ai_message.tool_calls`.
- **`ToolMessage`**: how a tool's result gets reported back into the
  conversation, labeled with which request it's answering.
- **the AI decides, your code executes**: the model can only ask, never
  directly run anything itself.

If anything here still feels unclear, ask before moving to Lesson 15.
