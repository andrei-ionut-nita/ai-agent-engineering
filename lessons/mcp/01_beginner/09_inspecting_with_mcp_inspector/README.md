# Lesson 9: The MCP Inspector

## A debugger for servers, before you write a client

Every lesson so far tested a server by writing a Python client for it.
That's the point eventually, but it's slow while you're still building
a server: right now you just want to see what a client *would* see.
The [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
is a standalone dev tool, maintained by the MCP project itself, that
connects to any server and lets you browse its tools, resources, and
prompts, and call them, without writing any client code.

## Running it

The Inspector is a Node package, run through `npx` (no separate
install needed, it downloads and runs on demand):

```bash
npx @modelcontextprotocol/inspector uv run python lessons/mcp/01_beginner/09_inspecting_with_mcp_inspector/server.py
```

This launches a local web UI (it prints a URL to open) that connects
to `server.py` over stdio, exactly the way a real host would, and
lets you click through its tools, call them with arguments, read its
resources, and fill in its prompts interactively.

## The `--cli` mode: scriptable, no browser

The Inspector also has a non-interactive CLI mode, useful when you
want a quick one-off check without opening a browser, or when
scripting a check into something like a test suite:

```bash
npx @modelcontextprotocol/inspector --cli \
    uv run python lessons/mcp/01_beginner/09_inspecting_with_mcp_inspector/server.py \
    --method tools/list
```

```bash
npx @modelcontextprotocol/inspector --cli \
    uv run python lessons/mcp/01_beginner/09_inspecting_with_mcp_inspector/server.py \
    --method tools/call --tool-name add --tool-arg a=2 --tool-arg b=3
```

The first prints the same tool metadata `mcp.list_tools()` showed you
back in Lesson 3, but now from the outside, over the real protocol. The
second actually calls `add`, returning `{"content": [...], "isError": false}`,
identical in shape to what `session.call_tool(...)` gave you in Lesson 7.

## Why bother, if you're about to write a client anyway

Two reasons. First, speed: checking a schema or a return value with the
Inspector is one command, no client script to write or debug. Second,
isolation: if something's wrong, the Inspector lets you rule the server
out (or in) before you start suspecting bugs in your own client code,
useful every time something in Lessons 11 onward doesn't behave the
way you expect.

## Running it

This lesson's `lesson.py` doesn't call the Inspector itself, it's a
manual, interactive tool you run from your terminal. Run the two
commands above against `server.py` in this folder, then run
`lesson.py` just to confirm the server the Inspector was talking to
behaves the same way from Python:

```bash
uv run python lessons/mcp/01_beginner/09_inspecting_with_mcp_inspector/lesson.py
```

## Checkpoint

- **MCP Inspector**: `npx @modelcontextprotocol/inspector <command>`, a
  standalone tool that connects to any MCP server and lets you browse
  and call its tools/resources/prompts without writing a client.
- **`--cli` mode**: a scriptable, non-interactive way to run the same
  checks, useful for quick one-off verification.
- The Inspector talks the exact same protocol a real client would,
  what it shows you is what any host would see.

If anything here still feels unclear, ask before moving to Lesson 10,
the beginner checkpoint project.
