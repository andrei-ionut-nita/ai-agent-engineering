# Lesson 19 (Checkpoint): Gemini Chatbot Over Two MCP Servers

## What this combines

- **Multiple servers** (Lesson 17): a notes server and a calculator
  server, connected through one `MultiServerMCPClient`.
- **LLM wiring** (Lesson 15): `get_tools()` converted to LangChain
  tools, bound to Gemini.
- **The full loop, across turns** (Lesson 16): an interactive chat loop
  where `messages` accumulates, so later questions can refer back to
  earlier answers.
- **Lifespan state** (Lesson 18): the notes server keeps its notes in
  proper app state, not a bare module-level dict, this time.

## The shape

Two small servers live in this folder: `notes_server.py` (`add_note`
and `list_notes`, backed by a lifespan-managed `NotesState`) and
`calculator_server.py` (the same `add` tool from earlier lessons).
`lesson.py` is an interactive terminal chatbot: it connects to both,
binds their combined tools to Gemini, and loops, reading a line of
input, running the model, running whatever tools it asks for, printing
the answer, repeating.

## A wrinkle from Lesson 16, resolved

`client.get_tools()` (Lessons 15-17) opens a fresh session per tool
call, fine for the stateless calculator, but wrong for the notes
server: its lifespan state would reset every call, and a second
`add_note` would get id `1` again instead of `2`. This lesson instead
opens one persistent session per server with `client.session(name)` +
`load_mcp_tools(session)`, held open for the whole conversation via an
`AsyncExitStack`, so the notes server's state survives across every
tool call in the chat, exactly as Lesson 18 intended.

This is deliberately close to the official MCP quickstart's own
client, the difference is the LLM side uses LangChain/Gemini (this
course's convention) instead of the raw Anthropic SDK, everything else,
connect, list tools, loop on user input, is the same shape.

## Running it

```bash
uv run python lessons/mcp/02_intermediate/19_intermediate_checkpoint_project/lesson.py
```

Try asking it to add a note, then ask it to add two numbers, then ask
it something that refers back to an earlier answer in the same
session, all three should work without restarting the script.

## Checkpoint

If this ran cleanly, you've built a real, working MCP-backed chatbot,
combining every piece from Lessons 11 through 18. The advanced tier
from here on is about transports beyond stdio, and about running a
server safely in front of tools you didn't write yourself.

If anything here still feels unclear, go back to whichever of Lessons
11-18 covered that piece before moving to Lesson 20.
