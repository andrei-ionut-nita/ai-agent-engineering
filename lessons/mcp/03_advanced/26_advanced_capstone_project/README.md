# Lesson 26 (Capstone): Task Manager, server and client, end to end

## What this combines

Every piece from this course, in one project:

- **Tools, resources, and prompts** (Lessons 2, 5, 6): `add_task`,
  `complete_task`, `list_tasks`; a `tasks://{id}` resource;
  a `summarize_tasks` prompt.
- **Lifespan-managed state** (Lesson 18): tasks live in a proper
  `TaskManagerState`, set up and torn down around the server's
  lifetime, not a bare module-level dict.
- **Error handling** (Lesson 7): completing a task that doesn't exist
  raises a clear error, `isError=True`, server keeps running.
- **Stderr-safe logging** (Lesson 8): every log line goes through
  `logging`, never `print()`.
- **Both transports** (Lesson 20): `server.py` runs over stdio by
  default, or over Streamable HTTP with `--transport streamable-http`,
  same code either way.
- **An LLM actually using it** (Lessons 15-16): `lesson.py` connects
  over stdio, wraps the tools with `langchain-mcp-adapters`, binds them
  to Gemini, and runs a real multi-turn conversation.

## The server

```bash
# stdio (what lesson.py connects to)
uv run python lessons/mcp/03_advanced/26_advanced_capstone_project/server.py

# or, over HTTP, exactly Lesson 20's pattern:
uv run python lessons/mcp/03_advanced/26_advanced_capstone_project/server.py --transport streamable-http
```

Both invocations run the exact same tools, resources, and prompt, only
the transport argument differs, this is the payoff of Lesson 20's
lesson that transport and data layers are separate concerns.

## The client

`lesson.py` runs a short scripted conversation against the server over
stdio: add a couple of tasks, complete one, ask the model to summarize
where things stand, all through Gemini deciding which tool to call and
when, the same loop from Lesson 16, just against a server with more
moving parts than a calculator.

Like Lesson 19, it holds one persistent session open for the whole
conversation (`client.session("tasks")` + `load_mcp_tools(session)`),
rather than the ephemeral, one-session-per-call `client.get_tools()`
from Lessons 15-17. A stateless calculator doesn't care either way,
but the Task Manager's lifespan state (Lesson 18) would reset every
call under the ephemeral pattern, a second `add_task` would get id `1`
again instead of `2`.

```bash
uv run python lessons/mcp/03_advanced/26_advanced_capstone_project/lesson.py
```

Requires `GOOGLE_API_KEY` in a `.env` file at the project root, same
as every LLM-backed lesson in this course.

## Where to go from here

This capstone is deliberately still small enough to read start to
finish in one sitting. A production version of this same server would
add: persistent storage instead of in-memory state (the `SqliteSaver`
pattern from `langgraph/02_intermediate/14_persistent_checkpointer`
generalizes here), real authentication if deployed over HTTP (Lesson
21), and tracing to see what the model actually did across a session
(`langgraph/03_advanced/32_tracing_and_observability`'s callback-handler approach
works for MCP-backed agents too). Every piece those additions would
build on, tools, resources, prompts, transports, error handling,
security, you've now built yourself, from scratch, in this course.

## Checkpoint

If this ran cleanly end to end, tools, a resource, a prompt, both
transports, and a real model making decisions across a conversation,
you've built a complete, working MCP server and client. That's the
whole protocol, client and server, from the ground up.
