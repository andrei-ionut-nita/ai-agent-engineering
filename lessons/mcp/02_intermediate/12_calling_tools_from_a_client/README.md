# Lesson 12: Calling tools from a client

## `call_tool`, the client-side mirror of `@mcp.tool()`

Once you have a `session` and know a tool's name and arguments (from
`list_tools()`, Lesson 11), calling it is one line:

```python
result = await session.call_tool("add", {"a": 2, "b": 3})
```

`call_tool` takes the tool's name and a dict of arguments matching its
`inputSchema`, and returns a `CallToolResult`.

## Reading a `CallToolResult`

```python
result.isError       # bool: did the tool fail?
result.content       # list[ContentBlock]: the actual output
result.structuredContent  # dict | None: typed output, if the tool declared one
```

You saw `isError` already in Lesson 7. `content` is always a *list*,
even for a tool that returns one plain value, because MCP allows a tool
to hand back several pieces of content at once (text plus an image,
say). For a simple tool like `add`, that list has exactly one
`TextContent` block:

```python
result.content == [TextContent(type="text", text="5")]
```

`structuredContent` is new: if a tool's return type is annotated (as
`add`'s is, `-> int`), FastMCP also includes a typed, structured version
of the result alongside the text, `{"result": 5}` here. Lesson 14 covers
content blocks and structured output in full; for now, know both exist
and `content` is the one you can always rely on being present.

## Arguments must match the schema

Call a tool with the wrong argument names or types, and the server
rejects the call before your function ever runs, the same validation
`langchain/13_defining_tools`'s `.args` schema exists to describe. Try
it deliberately in `lesson.py`, calling `add` with a missing argument,
to see what that failure looks like from the client's side.

## Running it

```bash
uv run python lessons/mcp/02_intermediate/12_calling_tools_from_a_client/lesson.py
```

## Checkpoint

- **`session.call_tool(name, arguments)`**: invokes a tool by name,
  arguments as a dict matching its `inputSchema`.
- **`CallToolResult.content`**: always a list of content blocks, even
  for a single plain value.
- **`CallToolResult.structuredContent`**: a typed version of the
  result, present when the tool's return type is annotated.
- A malformed argument dict fails validation server-side before your
  tool function ever runs.

If anything here still feels unclear, ask before moving to Lesson 13,
reading resources and prompts from a client.
