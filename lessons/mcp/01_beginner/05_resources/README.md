# Lesson 5: Resources, data instead of actions

## Tools do things, resources are things

Every tool so far *does* something: converts a number, adds two
values. A **resource** is different: it just hands back data for
context, nothing is "done," nothing changes. Think of it like reading a
file versus running a script.

```python
@mcp.resource("notes://today")
def today_note() -> str:
    """Today's note."""
    return "Buy milk."
```

`@mcp.resource(uri)` takes a URI instead of relying on the function
name. `notes://today` is not a real network address, it's just a
unique identifier the client uses to ask for this specific piece of
data later.

## Discovering and reading a resource

The same list/get pattern as tools, with different verbs:

- `resources/list` (here: `await mcp.list_resources()`): what resources
  exist?
- `resources/read` (here: `await mcp.read_resource(uri)`): give me the
  content at this URI.

```python
resources = await mcp.list_resources()
# [Resource(uri='notes://today', name='today_note', description="Today's note.", ...)]

content = await mcp.read_resource("notes://today")
# [ReadResourceContents(content='Buy milk.', mime_type='text/plain')]
```

## URI templates: parameterized resources

A resource's URI can include a placeholder, letting one function serve
many different resources:

```python
@mcp.resource("notes://{date}")
def note_for_date(date: str) -> str:
    """Get the note for a given date."""
    return f"Note for {date}: nothing yet."
```

Reading `notes://2026-08-03` calls this function with `date="2026-08-03"`,
the same way a URL path parameter works in a web framework. This is
how a server can expose an entire, dynamic dataset (every note you've
ever written) as one resource definition instead of one per item.

## When to use a resource instead of a tool

If an AI needs to *decide* to fetch something based on the
conversation, a tool works fine, that's the whole point of tool
calling. Resources exist for the other case: data a host wants to pull
in as context up front, or attach to a message, without the AI needing
to explicitly ask for it via a function call. The distinction matters
more to host applications (how they present context to a user) than to
the AI itself, but the primitive exists so a server can be explicit
about which of its data is "context to attach" versus "action to
decide on."

## Running it

```bash
uv run python lessons/mcp/01_beginner/05_resources/lesson.py
```

## Checkpoint

- **`@mcp.resource(uri)`**: exposes read-only data at a URI, no
  side effects.
- **`resources/list` / `resources/read`**: discovery and retrieval,
  the resource equivalent of `tools/list` / `tools/call`.
- **URI templates** (`notes://{date}`): one function can serve many
  resources, parameterized by the URI itself.
- Resources are for *context to read*, tools are for *actions to take*.

If anything here still feels unclear, ask before moving to Lesson 6,
prompts.
