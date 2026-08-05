# Lesson 17: One agent, several MCP servers

## Why this matters

Lesson 1 introduced the host/client picture with several clients, one
per server, feeding into a single host. Every lesson since has used
exactly one server. Real hosts, Claude Desktop, Claude Code, rarely
stop at one, a typical setup connects a filesystem server, a search
server, and a company-specific server all at once. This lesson is
where `MultiServerMCPClient` earns its name: it already accepted a
*dict* of servers back in Lesson 15, we just only ever put one entry in
it.

## Two servers, one client

```python
client = MultiServerMCPClient(
    {
        "calculator": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [str(calculator_server_script)],
        },
        "weather": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [str(weather_server_script)],
        },
    }
)
tools = await client.get_tools()
```

`get_tools()` now returns tools from *both* servers, flattened into one
list. The model doesn't need to know or care which server a given tool
came from, `bind_tools(tools)` works exactly as before, one flat list,
same as Lesson 15.

## Naming collisions

Two servers could, in principle, both expose a tool called `search`.
`get_tools()` accepts a `server_name` argument to fetch tools from just
one server if you need to disambiguate, and `MultiServerMCPClient`'s
`tool_name_prefix` option can prefix every tool name with its server's
label automatically. This lesson's two servers use distinct, specific
names (Lesson 4's advice), so no collision happens here, but it's worth
knowing the escape hatch exists once you're combining servers you don't
control.

## Running it

```bash
uv run python lessons/mcp/02_intermediate/17_connecting_to_multiple_servers/lesson.py
```

## Checkpoint

- **`MultiServerMCPClient({...})`**: the dict can hold any number of
  named servers, not just one.
- **`await client.get_tools()`**: returns every server's tools,
  flattened into a single list a model can be bound to.
- A model calling tools from two different servers looks no different,
  from the model's side, than calling tools from one.
- Specific tool names (Lesson 4) matter even more once servers you
  didn't write could be combined with your own.

If anything here still feels unclear, ask before moving to Lesson 18,
server-side state shared across calls.
