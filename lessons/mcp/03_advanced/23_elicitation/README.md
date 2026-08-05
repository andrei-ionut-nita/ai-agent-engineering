# Lesson 23: A server asking the user a question mid-call

## The direction of communication flips here

Every primitive so far flows one way: the client asks a server for
something. **Elicitation** is the opposite: a server, mid-tool-call,
asks the *user* something and waits for an answer before continuing.
Think "are you sure you want to delete this?", except the confirmation
dialog is defined by the server, not hardcoded into your client.

## Declaring what the server needs

```python
from pydantic import BaseModel, Field
from mcp.server.fastmcp import Context, FastMCP


class ConfirmDeletion(BaseModel):
    confirm: bool = Field(description="Type true to confirm deletion.")


@mcp.tool()
async def delete_file(filename: str, ctx: Context) -> str:
    """Delete a file, after asking the user to confirm."""
    result = await ctx.elicit(
        message=f"Really delete '{filename}'?",
        schema=ConfirmDeletion,
    )
    if result.action != "accept" or not result.data.confirm:
        return "Deletion cancelled."
    return f"Deleted '{filename}'."
```

`schema` is a Pydantic model, the same idea as a tool's `inputSchema`
(Lesson 3), just describing what shape of answer the server expects
back from the *user* this time, not from the AI. `ctx.elicit(...)`
sends the question and suspends the tool call until a response
arrives.

## Answering it on the client

A client that wants to support elicitation supplies an
`elicitation_callback`:

```python
import mcp.types as types


async def elicitation_callback(context, params):
    print("Server is asking:", params.message)
    # A real client would show a UI dialog here. This one auto-confirms.
    return types.ElicitResult(action="accept", content={"confirm": True})


async with ClientSession(read, write, elicitation_callback=elicitation_callback) as session:
    ...
```

`action` is one of `"accept"`, `"decline"`, or `"cancel"`, giving the
server a clear three-way answer rather than just true/false: declining
answers "no", cancelling means "stop asking me things entirely for
this call." A client that doesn't provide a callback rejects every
elicitation automatically, the server always gets a definite answer,
never hangs waiting.

## Running it

```bash
uv run python lessons/mcp/03_advanced/23_elicitation/lesson.py
```

This runs `delete_file` twice: once with a callback that accepts, once
with one that declines, so you can see both branches of the tool's
logic actually execute.

## Checkpoint

- **Elicitation** is server-to-user, the one primitive in this course
  that flows the opposite direction from every other.
- **`ctx.elicit(message, schema)`**: suspends a tool call, asking the
  user for a specific, schema-shaped answer.
- **`elicitation_callback`**: the client-side handler that actually
  answers, `action` is `"accept"`, `"decline"`, or `"cancel"`.
- No callback means every elicitation is automatically rejected, never
  a hang.

If anything here still feels unclear, ask before moving to Lesson 24,
security.
