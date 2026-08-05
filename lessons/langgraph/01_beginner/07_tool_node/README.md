# Lesson 7: ToolNode and tools_condition, the think/act loop by hand

## Where we left off

Lesson 6's graph could only ever produce one model reply and stop. Real
usefulness often needs the model to call a tool, see the result, and
respond based on it, the "think, act, think again" loop that
`create_agent` (Lesson 23 of the LangChain course, which you've already
seen) automates for you. This lesson builds that exact loop by hand,
using LangGraph's own building blocks, so you understand precisely what
`create_agent` is doing underneath. Lesson 23 of this course revisits
the same idea in a more general form.

## The pieces

```python
@tool
def get_word_length(word: str) -> int:
    """Return the number of characters in a word."""
    return len(word)


model_with_tools = model.bind_tools([get_word_length])
```

Nothing new here versus the LangChain course: `@tool` turns a function
into something a model can be told about, and `.bind_tools()` makes the
model aware it's allowed to request that tool instead of answering
directly. When the model decides a tool is needed, `.invoke()` still
returns an `AIMessage`, but one with a non-empty `.tool_calls` list
instead of (or alongside) written text.

```python
tool_node = ToolNode(tools=[get_word_length])
```

`ToolNode` is a node LangGraph provides ready-made: give it a list of
tools, and it knows how to read the most recent `AIMessage`'s
`tool_calls`, actually run the matching Python function(s), and return
the results as `ToolMessage` objects, appended to `messages` just like
any other node output. Registered under the default name `"tools"`
unless you pass a different name.

```python
builder.add_conditional_edges("call_model", tools_condition)
```

`tools_condition` is a routing function LangGraph provides, so you don't
have to write your own version of Lesson 4's routing logic every time.
It inspects the latest message: if it has pending tool calls, it returns
`"tools"` (the `ToolNode`'s name), if not, it returns `"__end__"`, ending
the graph. This is the exact decision a hand-rolled `if
ai_message.tool_calls:` check would make, just packaged for you.

```python
builder.add_edge("tools", "call_model")
```

Here's the loop, same idea as Lesson 5: after the tool runs, route back
to `call_model` so the model can see the tool's result and decide what
to do next; answer directly, or ask for another tool call. That second
possibility is why this is a loop and not just a detour, in principle
the model could call several tools across several rounds before it's
ready to answer, this lesson keeps it to one tool and lets it run until
it settles, so the shape stays easy to follow.

## Running it

```bash
uv run python lessons/langgraph/01_beginner/07_tool_node/lesson.py
```

Watch the printed messages: a human question, an AI message with a tool
call and no visible answer yet, a tool result, then a final AI message
that actually answers using that result.

## Checkpoint

- **`ToolNode`**: a ready-made node that runs whichever tools the most
  recent `AIMessage` requested, and returns the results as
  `ToolMessage`s.
- **`tools_condition`**: a ready-made routing function, `"tools"` if the
  last message has pending tool calls, otherwise ends the graph.
- **the think/act loop**: `call_model -> tools -> call_model -> ...`,
  the same cycle idea from Lesson 5, now doing real work.
- **this is what `create_agent` automates**: the LangChain course's
  `create_agent` (Lesson 23 there) builds exactly this loop for you;
  this lesson shows what's happening underneath it.

If anything here still feels unclear, ask before moving to Lesson 8.
