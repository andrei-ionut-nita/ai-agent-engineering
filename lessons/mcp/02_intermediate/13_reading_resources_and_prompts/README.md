# Lesson 13: Reading resources and prompts from a client

## Same shape, different verbs

`call_tool` was the client-side mirror of `@mcp.tool()`. Resources and
prompts (Lessons 5 and 6) have their own matching pairs:

```python
resources = await session.list_resources()
content = await session.read_resource("notes://today")

prompts = await session.list_prompts()
filled_in = await session.get_prompt("code_review", {"language": "python", "code": "print(1)"})
```

## Reading a resource

```python
result = await session.read_resource("notes://today")
result.contents  # list[TextResourceContents | BlobResourceContents]
```

Like tool content, `contents` is a list, a resource can be made of
several distinct pieces. Each item has a `.uri`, a `.mimeType`, and
either `.text` (for text resources) or `.blob` (for binary ones,
base64-encoded).

## Getting a filled-in prompt

```python
result = await session.get_prompt("code_review", {"language": "python", "code": "print(1)"})
result.messages  # list[PromptMessage]
```

`messages` is the list of `PromptMessage` objects you first saw
server-side in Lesson 6: each has a `.role` (`"user"` or `"assistant"`)
and `.content`. A prompt template can hand back several messages at
once, letting a server ship a whole scripted conversation opener, not
just a single line.

## Why a client needs both

A tool-only client is common, most of this course focuses there,
because "let the AI decide what to call" is the dominant use case. But
a host application (think Claude Desktop's UI, or your own chatbot in
Lesson 15) often wants to *show a user* what resources or prompt
templates a server offers, as attachable context or a picklist of
starting points, independent of whatever the AI itself decides to do.
Reading resources and prompts is how a client supports that.

## Running it

```bash
uv run python lessons/mcp/02_intermediate/13_reading_resources_and_prompts/lesson.py
```

## Checkpoint

- **`session.list_resources()` / `session.read_resource(uri)`**: the
  client-side mirror of `@mcp.resource()`.
- **`session.list_prompts()` / `session.get_prompt(name, args)`**: the
  client-side mirror of `@mcp.prompt()`.
- A resource's `contents` and a prompt's `messages` are both lists,
  same reasoning as a tool's `content`: one primitive can hand back
  several pieces at once.

If anything here still feels unclear, ask before moving to Lesson 14,
a closer look at content blocks.
