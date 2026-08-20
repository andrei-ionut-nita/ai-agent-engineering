# Lesson 1: What Langflow is, and getting it running on your machine

## Where this course sits

Every other course in this project builds agents in code: you write
`.invoke()` calls, wire `StateGraph` nodes and edges by hand, define
tools as decorated Python functions. That's the right tool once you
know what you're building. Langflow is for the step before that: a
visual canvas where the same building blocks, prompts, models, tools,
memory, become boxes you drag and connect, so you can shape a flow by
eye before committing it to code. It's built on the same ideas
`langchain` and `langgraph` already taught you, a "component" here is
close kin to a LangChain runnable, an edge on the canvas is close kin to
a LangGraph edge, this course spends its time on what the visual layer
adds (and costs), not re-teaching those ideas from zero.

## What Langflow actually is

Langflow is an open-source (MIT-licensed), self-hosted application: a
local web server with a drag-and-drop canvas in the browser, and a
Python package underneath it you can call directly from code. Every
flow you build, a set of connected components, is really just a graph,
the same shape as a LangGraph graph, described as JSON instead of
Python. That JSON is the artifact this whole course keeps coming back
to: it's what the canvas edits, what gets checked into git, and what a
script loads to run the same flow with no browser involved at all.

## Getting it running

Langflow was added to this project's dependencies (`langflow` in
`pyproject.toml`), so `uv sync` already installed it. Start the server
yourself, in its own terminal, and leave it running for the rest of
this course, the same way the `redis`/`pgvector`/`pggraph` courses have
you leave `docker compose up -d` running in the background:

```bash
uv run langflow run --no-open-browser
```

The first start takes a few seconds (it's setting up a local SQLite
database for your flows). Once you see `Open Langflow -> http://localhost:7860`
in the terminal, open that URL in your browser. You'll land straight on
the flows dashboard, no login screen, this is `LANGFLOW_AUTO_LOGIN`
(on by default for a local install) signing you in as a default local
user automatically. Leave this tab open, later lessons have you come
back to it.

## Do this yourself

1. Run `uv run langflow run --no-open-browser` in a terminal and leave
   it running.
2. Open `http://localhost:7860` in your browser.
3. Confirm you land on a flows dashboard (not a login form) - that's
   auto-login working.

## The code, piece by piece

```python
response = httpx.get("http://127.0.0.1:7860/health_check")
```

Langflow exposes its own health endpoint, the same idea as Redis's
`PING` in the `redis` course: a cheap call that proves the server is up
and its database connection is working, before anything else in this
course tries to talk to it. `health_check` (as opposed to the simpler
`/health`) also reports on the chat service and the database
specifically, which is what actually matters for every later lesson.

## Running it

```bash
uv run langflow run --no-open-browser   # in its own terminal, leave it running
uv run python lessons/langflow/01_beginner/01_what_is_langflow/lesson.py
```

## Expected output

```
Langflow 1.10.3 is up at http://127.0.0.1:7860
health_check -> {'status': 'ok', 'chat': 'ok', 'db': 'ok'}
```

(The version number will match whatever `langflow` version `uv sync`
installed for you, that's fine, it doesn't need to match exactly.) If
you see a connection error instead, go back and confirm `langflow run`
is still running in its own terminal.

## Checkpoint

- **Langflow**: an open-source, self-hosted app, a visual canvas over a
  Python package, every flow is a graph described as JSON underneath.
- **`langflow run`**: starts the local server, kept running in its own
  terminal for the whole course, the same pattern as `docker compose up -d`
  in the Redis/pgvector/pggraph courses.
- **auto-login**: a local install signs you in automatically, no
  credentials to manage for this course.
- **`/health_check`**: the cheapest possible "is it up, and is its
  database working" call, worth reaching for whenever a later lesson's
  request fails unexpectedly.

If anything here still feels unclear, ask before moving to Lesson 2.
