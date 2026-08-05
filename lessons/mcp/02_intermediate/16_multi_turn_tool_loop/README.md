# Lesson 16: The full ask/call/respond loop

## Closing the loop from Lesson 15

Lesson 15 got as far as the model deciding to call `add`. Now we
actually run it and hand the result back, the same three-step loop
from `langchain/14_tool_calling`, just with an MCP-backed tool instead
of a local one:

```python
messages = [HumanMessage("What is 12 plus 30?")]
response = model.invoke(messages)
messages.append(response)

for call in response.tool_calls:
    tool = tools_by_name[call["name"]]
    result = await tool.ainvoke(call["args"])
    messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

final = model.invoke(messages)
```

`ToolMessage` carries the result back with `tool_call_id` matching the
original call, so the model can line up which result answers which
request, identical to how `langchain/14_tool_calling` closed its loop.

## A detail specific to `MultiServerMCPClient`

Watch the logs while this runs: you'll see the server's `tools/list`
handler fire more than once. `MultiServerMCPClient` opens a fresh
connection to the server for *each* tool call, rather than holding one
session open across the whole conversation. For a stdio server, that
means a new subprocess launch per call. This is a real cost (slower
than a persistent connection) that the adapter accepts in exchange for
never needing you to manage a session's lifetime by hand, fine for a
calculator, worth knowing about before you build something
call-heavy.

## Multiple turns, one conversation

The `messages` list is the same running conversation history from
`langchain/17_conversation_memory`: each turn appends to it rather than
starting fresh, so a second question can refer back to the first one's
answer. `lesson.py` asks two questions in the same conversation to
show this.

## Running it

```bash
uv run python lessons/mcp/02_intermediate/16_multi_turn_tool_loop/lesson.py
```

## Checkpoint

- The MCP tool-calling loop is identical in shape to LangChain's local
  one: invoke, read `tool_calls`, run each tool, append a
  `ToolMessage`, invoke again.
- **`MultiServerMCPClient` opens a new session per tool call**, a
  real, visible cost specific to this adapter, not a general MCP
  property.
- Appending to a running `messages` list carries context across turns,
  the same mechanism as `langchain/17_conversation_memory`.

If anything here still feels unclear, ask before moving to Lesson 17,
talking to more than one server at once.
