# Lesson 15: Handing MCP tools to an LLM

## The missing piece

Everything through Lesson 14 called tools *yourself*, with hardcoded
names and arguments. The whole point of MCP, though, is letting an AI
decide which tool to call and with what arguments, exactly like
`langchain/14_tool_calling` did with local `@tool` functions. This
lesson connects those two worlds: MCP tools on one side, a LangChain
model on the other.

## `langchain-mcp-adapters`: the bridge

`langchain-mcp-adapters` converts MCP tools into ordinary LangChain
`BaseTool` objects, so anything you already know how to do with
`bind_tools` just works:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "calculator": {
        "transport": "stdio",
        "command": "python",
        "args": [str(server_script)],
    }
})
tools = await client.get_tools()
```

`MultiServerMCPClient` takes a dict of named server connections
("calculator" is just a label you choose) and `get_tools()` launches
each server, lists its tools, and wraps every one as a LangChain tool.
Notice there's no manual `stdio_client`/`ClientSession` here, the
adapter manages the connection lifecycle for you.

## `bind_tools`, same as always

```python
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite").bind_tools(tools)
response = model.invoke("What is 12 plus 30? Use the tool.")
response.tool_calls
# [{"name": "add", "args": {"a": 12, "b": 30}, "id": "...", "type": "tool_call"}]
```

This is identical to `langchain/14_tool_calling`. The model has no idea
these tools came from a separate server over a protocol, it just sees
LangChain tools with a name, description, and schema, precisely the
"the AI never sees the implementation" principle from Lesson 3, now
crossing a process boundary and a LangChain adapter on its way to
Gemini.

## What this lesson doesn't do yet

Gemini decided to call `add`, but nothing here actually *executes* that
call and feeds the result back. That loop, ask, call, respond, is
exactly `langchain/14_tool_calling`'s manual loop, and it's Lesson 16's
subject.

## Running it

```bash
uv run python lessons/mcp/02_intermediate/15_wiring_an_llm_to_mcp_tools/lesson.py
```

## Checkpoint

- **`MultiServerMCPClient`**: manages one or more MCP server
  connections and exposes their tools as LangChain tools.
- **`await client.get_tools()`**: launches each configured server,
  lists its tools, wraps them, returns one flat list.
- Once wrapped, an MCP tool is indistinguishable from a local `@tool`
  to `bind_tools` and the model, same interface, different origin.
- The model deciding to call a tool and the tool actually being called
  are two separate steps, this lesson is only the first.

If anything here still feels unclear, ask before moving to Lesson 16,
completing the loop.
