# Lesson 21: Pydantic AI as an MCP client

## Reusing everything you built in the `mcp` course

The `mcp` course built servers and a LangChain-based client
(`langchain-mcp-adapters`). Pydantic AI has its own first-class MCP
client, `MCPToolset`, so any MCP server you already built, or any
third-party one, becomes a normal set of agent tools with no adapter
library needed.

## Connecting to a server

`StdioTransport` launches a server as a subprocess and speaks MCP over
its stdin/stdout, exactly the transport covered through `mcp` Lesson
19. `MCPToolset` wraps that transport as something an `Agent` accepts
directly in its `toolsets=` list:

```python
from pydantic_ai.mcp import MCPToolset, StdioTransport

transport = StdioTransport(command=sys.executable, args=[str(server_script)])
toolset = MCPToolset(transport)

agent = Agent("google:gemini-3.5-flash-lite", toolsets=[toolset])
```

## Why `async with agent:`

MCP servers are external processes with a real connection lifecycle,
start the subprocess, initialize the protocol handshake, eventually
tear it down. Wrapping your runs in `async with agent:` opens that
connection once and keeps it open for every `run`/`run_sync` call
inside the block, then cleans it up automatically on exit:

```python
async with agent:
    result = await agent.run("What is 2 plus 3? Use a tool.")
    print(result.output)
```

Without the context manager, Pydantic AI would have to start and stop
the server subprocess on every single call, which works but is wasteful
for anything beyond a one-off script.

## What the agent actually sees

From the model's point of view, `add` and `multiply` (defined in this
lesson's `server.py`, a small `FastMCP` server) look exactly like any
`@agent.tool_plain` function from Lesson 6, same schema-from-type-hints
mechanism, just discovered over MCP's `tools/list` instead of read off
a local Python function. This is the payoff of MCP as a protocol: the
same server this lesson connects to could equally be wired into
Claude Desktop, Claude Code, or a LangChain agent, no rewriting needed
on the server side.

## Running it

```bash
uv run python lessons/pydantic_ai/03_advanced/21_pydantic_ai_as_mcp_client/lesson.py
```

## Checkpoint

- `StdioTransport` + `MCPToolset` is Pydantic AI's native MCP client,
  no separate adapter library needed.
- `toolsets=[toolset]` on `Agent(...)` makes an MCP server's tools
  available exactly like local `@agent.tool` functions.
- `async with agent:` manages the server subprocess's lifecycle for
  the whole block, rather than per call.

If anything here still feels unclear, ask before moving to Lesson 22.
