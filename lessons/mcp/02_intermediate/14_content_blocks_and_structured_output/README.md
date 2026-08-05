# Lesson 14: Content blocks, and why `content` is always a list

## The question this answers

Every result so far had `content` be a one-item list: `[TextContent(text="5")]`.
It would be reasonable to wonder why it's a list at all, instead of
just a string. This lesson is the answer: a single tool call can return
*more than one kind of content at once*.

## Returning more than text

`FastMCP` recognizes a few return shapes beyond a plain string. To
return an image, use the `Image` helper:

```python
from mcp.server.fastmcp import FastMCP, Image

@mcp.tool()
def make_thumbnail() -> Image:
    """Return a small PNG thumbnail."""
    png_bytes = render_thumbnail()  # however you produce the bytes
    return Image(data=png_bytes, format="png")
```

The client receives an `ImageContent` block instead of `TextContent`,
with `.mimeType` (`"image/png"`) and `.data` (base64-encoded bytes)
instead of `.text`.

## Returning several blocks at once

Return a list, and each item becomes its own content block, mixed
types allowed:

```python
@mcp.tool()
def make_thumbnail_with_caption() -> list:
    """Return a caption and a thumbnail together."""
    return ["Here is your thumbnail:", Image(data=png_bytes, format="png")]
```

```python
result.content
# [TextContent(text="Here is your thumbnail:"), ImageContent(mimeType="image/png", data="...")]
```

This is the actual reason `content` is a list everywhere in this
course, one tool call, one API response, but potentially several
distinct pieces of content, exactly like a chat message from a
multimodal model can contain both text and an image in the same turn.

## `structuredContent`: the typed escape hatch

Lesson 12 mentioned `structuredContent` briefly. When a tool's return
type is a simple annotated type (`int`, a `TypedDict`, a Pydantic
model), FastMCP includes a second, machine-readable version of the
result alongside the human-readable `content`:

```python
result.content            # [TextContent(text="5")]
result.structuredContent  # {"result": 5}
```

`content` is what you show a human or feed back to a model as
conversation text. `structuredContent` is what your own code should
read when it needs the actual typed value, no string-parsing required.

## Running it

```bash
uv run python lessons/mcp/02_intermediate/14_content_blocks_and_structured_output/lesson.py
```

## Checkpoint

- **`Image`**: a helper for returning image content from a tool,
  `data` plus `format`.
- Returning a **list** from a tool produces multiple, possibly
  mixed-type, content blocks in one result.
- **`content`**: always a list, this lesson is why, one call can return
  several distinct pieces of content.
- **`structuredContent`**: a typed, machine-readable version of a
  tool's result, present when the return type is annotated.

If anything here still feels unclear, ask before moving to Lesson 15,
where an LLM starts deciding which tools to call.
