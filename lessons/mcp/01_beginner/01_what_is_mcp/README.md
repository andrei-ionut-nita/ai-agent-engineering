# Lesson 1: What is MCP?

## The problem MCP solves

In the `langchain` course, every tool an AI could use was a Python
function living in the same process as the AI: `@tool`, `bind_tools`,
done. That works great until the tool needs to live somewhere else,
maintained by someone else. Your calendar, a company's ticketing
system, a database you don't control: none of that can be "just a
Python function you import."

MCP (Model Context Protocol) is a standard way to expose tools, data,
and prompt templates from one program to another, over a real
protocol, so an AI application doesn't need custom integration code for
every single service it wants to use. Anthropic describes it as "a USB-C
port for AI applications": one connector shape, many devices on either
end.

## Host, client, server

MCP has three participants, and the names are precise:

- **Host**: the AI application itself. Claude Desktop, Claude Code, or
  a chatbot you build in Lesson 15, is a host.
- **Client**: an object the host creates, one per server, that holds
  the connection open and speaks the protocol. A host talking to three
  servers has three clients internally.
- **Server**: the program that actually exposes tools, resources, and
  prompts. This is what you'll build first, starting in Lesson 2.

A server can run locally as a subprocess your host launches (the
**stdio transport**, covered through Lesson 19) or remotely over HTTP
(the **Streamable HTTP transport**, covered starting in Lesson 20).
Either way, the host talks to it through the same client interface.

## The three primitives a server exposes

- **Tools**: functions the AI can call to *do* something (send an
  email, run a query). Exactly like `@tool` in the langchain course,
  just served over a protocol instead of imported directly.
- **Resources**: data the AI can *read* for context (a file, a
  database row, an API response), without calling a function to "do"
  anything.
- **Prompts**: reusable, pre-written templates a user or host can pull
  up to start an interaction in a structured way.

You'll build one of each in Lessons 2, 5, and 6.

## JSON-RPC, briefly

Underneath all of this, a client and server exchange JSON-RPC 2.0
messages: a `method` name, some `params`, and (for requests, not
notifications) a matching response keyed by `id`. You will never write
this JSON by hand, the SDK handles it, but it's worth seeing once so
"list the tools" and "call this tool" stop being magic:

```python
{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
```

```python
{"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": "calculator", "...": "..."}]}}
```

`tools/list` asks "what can you do?", `tools/call` asks "do this one,
with these arguments." Resources and prompts have their own matching
`resources/list` / `resources/read` and `prompts/list` / `prompts/get`
pairs. Every lesson from here on is really just a thin, typed wrapper
around requests that look like this.

## Running it

This lesson has no server or client yet, just a script that prints the
mental model out so it's fixed in your head before Lesson 2 builds a
real server.

```bash
uv run python lessons/mcp/01_beginner/01_what_is_mcp/lesson.py
```

## Expected output

No network calls here, just printed vocabulary, so this is exact:

```
MCP participants:
  Host: The AI application. Claude Desktop, Claude Code, or a chatbot you build yourself in Lesson 15.
  Client: One per server, created by the host, holds the connection open and speaks the protocol.
  Server: The program exposing tools, resources, and prompts. What you build starting in Lesson 2.

MCP server primitives:
  Tools: Functions the AI can call to DO something. Discovered with tools/list, invoked with tools/call.
  Resources: Data the AI can READ for context, no action taken. Discovered with resources/list, fetched with resources/read.
  Prompts: Reusable interaction templates. Discovered with prompts/list, filled in with prompts/get.

Transport: stdio (local subprocess, Lessons 2-19) or Streamable HTTP (remote server, Lessons 20+). Same protocol either way, just a different pipe underneath.
```

If you see an error instead, check the
[Troubleshooting section](../../../../README.md#troubleshooting) in
this project's root README.

## Checkpoint

- **host**: the AI application (Claude Desktop, Claude Code, your own
  chatbot).
- **client**: the host's connection object to one specific server.
- **server**: the program exposing tools/resources/prompts.
- **tools** vs **resources** vs **prompts**: do something, read
  something, reusable template.
- **stdio vs Streamable HTTP**: local subprocess vs remote network
  server, same protocol either way.

If anything here still feels unclear, ask before moving to Lesson 2,
where we build a real server.
