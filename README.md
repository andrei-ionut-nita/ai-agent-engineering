# ai-agent-engineering

[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue)](.python-version)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![uv](https://img.shields.io/badge/managed%20with-uv-purple)](https://docs.astral.sh/uv/)

A hands-on LangChain, LangGraph, LangSmith, MCP, LlamaIndex, LiteParse,
MarkItDown, Docling, pgvector, pggraph, Pydantic AI, Ollama, Playwright,
and Redis course, built as small, linear lessons, Beginner through
Advanced. Each lesson is one focused concept: a short `README.md` to
read, then a `lesson.py` to run. No Python experience required going
in, comfort in any programming language is enough, Python's own syntax
and idioms are taught inline, in comments, right where they first show
up in each lesson.

Fourteen courses, meant to be done in order:

- **[lessons/langchain](lessons/langchain/)** (35 lessons): prompts,
  chains, tools, agents, RAG.
- **[lessons/langgraph](lessons/langgraph/)** (35 lessons): the graph
  engine LangChain's own agents are built on, memory, persistence,
  multi-agent systems.
- **[lessons/langsmith](lessons/langsmith/)** (23 lessons): tracing,
  datasets, evaluation, and monitoring for the agents built in the
  other two courses.
- **[lessons/mcp](lessons/mcp/)** (26 lessons): the Model Context
  Protocol, building MCP servers (tools, resources, prompts) and MCP
  clients, then wiring MCP tools into a LangChain/Gemini agent.
- **[lessons/llamaindex](lessons/llamaindex/)** (24 lessons): the other
  major open-source RAG/agent framework, data-centric where LangChain
  is chain-centric, indexes, query engines, agents, and swapping tools
  between the two frameworks.
- **[lessons/liteparse](lessons/liteparse/)** (14 lessons): a local,
  open-source, Rust-backed PDF parser, layout, form fields, OCR
  fallback for scanned documents, and no API key or cloud service.
- **[lessons/markitdown](lessons/markitdown/)** (12 lessons): Microsoft's
  open-source "convert anything to Markdown" library, Word, Excel,
  PowerPoint, images, and URLs, feeding a real RAG pipeline.
- **[lessons/docling](lessons/docling/)** (18 lessons): IBM's
  open-source document-conversion library, layout analysis, table
  structure recognition, OCR, chunking for RAG, and enrichment
  pipelines for formulas, code, and pictures.
- **[lessons/pgvector](lessons/pgvector/)** (28 lessons): Postgres as a
  vector database, indexing, hybrid search, and production-shaped RAG.
- **[lessons/pggraph](lessons/pggraph/)** (29 lessons): Postgres as a
  graph database, registering tables and edges, traversal, shortest
  path, GQL/Cypher queries, and relationship-aware retrieval for AI
  agents.
- **[lessons/pydantic_ai](lessons/pydantic_ai/)** (24 lessons): a
  type-safe agent framework built around validated Python types instead
  of strings, tools, dependency injection, multi-agent delegation,
  evals, and MCP, the same ideas as the other courses through a
  different, more strict lens.
- **[lessons/ollama](lessons/ollama/)** (24 lessons): running
  open-source LLMs locally, no API key or per-token cost, structured
  output and tool calling on local models, and a fully offline RAG
  agent.
- **[lessons/playwright](lessons/playwright/)** (24 lessons): browser
  automation as an agent tool, navigating and reading real pages,
  filling in forms, and a capstone web research agent.
- **[lessons/redis](lessons/redis/)** (24 lessons): fast, ephemeral
  agent state, session memory, response caching, rate limiting,
  pub/sub streaming, and vector search.

## Quick start

Already have `uv` and Python 3.14? This is the whole setup:

```bash
uv sync
cp .env.example .env   # then add your GOOGLE_API_KEY, see Setup below
uv run python lessons/langchain/01_beginner/01_first_call/lesson.py
```

New to any of these tools? Keep reading, [Prerequisites](#prerequisites)
and [Setup](#setup) below cover everything from scratch.

## Prerequisites

You need three tools installed on your machine before any of this
works. If you already have them, skip to [Setup](#setup).

- **Python 3.14** (see `.python-version`). If you don't have it, the
  easiest path is to install `uv` first (below), then run `uv python
  install 3.14`, which downloads a matching Python for you, you don't
  need to install Python separately or manage it yourself.
- **`uv`**: the package manager and script runner every lesson's
  "Running it" command uses. It replaces `pip` + `venv` with one tool
  that also manages the Python version. Install it with:

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  (see [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)
  for other platforms, including Windows). After installing, close and
  reopen your terminal, then confirm it worked with `uv --version`.
- **Docker** (needed only for the pgvector, pggraph, and redis
  courses): runs Postgres and Redis in isolated containers instead of
  you installing them directly on your machine. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
  (Mac/Windows) or `docker.io`/`docker-ce` via your package manager
  (Linux), then confirm it worked with `docker --version`.
- **Ollama** (needed only for the ollama course): runs open-source
  LLMs locally. Install from [ollama.com/download](https://ollama.com/download),
  then confirm it worked with `ollama --version`. See
  [lessons/ollama/README.md](lessons/ollama/README.md) for pulling
  your first model.

If you're new to the terminal: every code block in this repo's READMEs
that starts with `$` or a bare command like `uv run ...` is meant to be
typed into a terminal window, opened in this project's root folder
(the one containing this `README.md`), not into Python or a text
editor.

## Setup

```bash
uv sync
```

This reads `pyproject.toml` and `uv.lock`, downloads the exact Python
version and every package version this project was built against, and
installs them into a project-local virtual environment (a `.venv`
folder), isolated from anything else on your machine. `uv run` (used in
every lesson) automatically uses that environment, so you never
activate it by hand.

Then create a `.env` file in this directory with a free Gemini API key
(get one at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)):

```
GOOGLE_API_KEY=your-key-here
```

Every lesson runs on Gemini specifically: its free tier needs no credit
card and is generous enough to work through the whole course on, which
is why this repo standardizes on one provider instead of asking you to
juggle several API keys from day one. The langchain course's Lesson 11
(`init_chat_model`) still teaches that the code underneath is
provider-agnostic and swappable, Gemini is a practical choice for
learning, not a hard dependency of the concepts themselves.

A `.env` file is a plain text file of `KEY=value` pairs that
`load_dotenv()` reads into your program at startup, so secrets like API
keys live in one untracked file instead of being typed into source code
(`.gitignore` already excludes `.env`; only `.env.example`, which has no
real keys, is committed). Copy `.env.example` to `.env` as a starting
point if you like.

For the langsmith course, also add a free LangSmith API key (get one at
[smith.langchain.com](https://smith.langchain.com)):

```
LANGSMITH_API_KEY=your-key-here
LANGSMITH_TRACING=true
```

For the pgvector course, you also need a local Postgres with the
pgvector extension, started via Docker Compose:

```bash
docker compose up -d
```

This reads `POSTGRES_DSN` from `.env` (see `.env.example`) and starts
Postgres on `localhost:5433`.

For the pggraph course, the same `docker compose up -d` also starts a
second, separate Postgres, this one with the pggraph extension
pre-installed, on `localhost:5434`. This reads `PGGRAPH_DSN` from
`.env`. It's a different container and image from the pgvector one
above (pggraph needs its own database, literally named `graph`), the
two run side by side and don't interfere with each other.

For the redis course, the same `docker compose up -d` also starts a
`redis-stack-server` container on `localhost:6379`. This reads
`REDIS_DSN` from `.env` (see `.env.example`). The "stack" image, not
plain `redis`, is used because the course's advanced lessons need the
`RedisJSON` and `RediSearch` modules it ships with.

For the playwright course, `uv sync` installs the Python package, but
the browser binaries themselves are a separate one-time download:

```bash
uv run playwright install chromium
```

Run any lesson from the project root, for example:

```bash
uv run python lessons/langchain/01_beginner/01_first_call/lesson.py
```

## Troubleshooting

- **`ModuleNotFoundError`**: you ran `python` directly instead of `uv
  run python`, or haven't run `uv sync` yet. `uv run` is what puts the
  installed packages on the path, a plain `python`/`python3` command
  won't see them.
- **`KeyError: 'GOOGLE_API_KEY'` or a 401/403 from Google**: your `.env`
  file is missing, misspelled, or not in the project root (it must sit
  next to this `README.md`, not inside `lessons/`). Double check there
  are no quotes or spaces around the value, `GOOGLE_API_KEY=abc123`, not
  `GOOGLE_API_KEY = "abc123"`.
- **429 / rate limit / resource exhausted errors from Gemini**: the free
  tier caps requests per minute and per day. Wait a minute and rerun; if
  it persists, you've hit the daily cap and need to wait for it to
  reset. This is expected occasionally while learning, not a bug in the
  lesson.
- **`connection refused` / `could not connect to server` (pgvector or
  pggraph course)**: Postgres isn't running. Run `docker compose up -d`
  from the project root, then `docker ps` to confirm both containers are
  up before rerunning the lesson.
- **`port is already allocated` when running `docker compose up -d`**:
  something else on your machine is already using port `5433` (pgvector)
  or `5434` (pggraph). Stop that other process, or change the port
  mapping in `docker-compose.yml` and the matching `POSTGRES_DSN` /
  `PGGRAPH_DSN` in `.env` to match.
- **`redis.exceptions.AuthenticationError` or `ConnectionError`
  (redis course)**: Redis isn't running, or `REDIS_DSN` doesn't match
  the password set in `docker-compose.yml`. Run `docker compose up -d`
  and confirm `docker ps` shows the `redis` service healthy.
- **`ollama: command not found` or connection refused on
  `localhost:11434` (ollama course)**: Ollama isn't installed or its
  background service isn't running. Reinstall from
  [ollama.com/download](https://ollama.com/download); on Linux you may
  need to start it manually with `ollama serve` in a separate terminal.
- **`Executable doesn't exist` (playwright course)**: browser binaries
  haven't been downloaded yet. Run `uv run playwright install
  chromium` from the project root.
- **`FATAL: database "graph" does not exist` (pggraph course)**: the
  pggraph image's own startup scripts require its database to be named
  literally `graph`, don't change `POSTGRES_DB` for the `graph_db`
  service in `docker-compose.yml`, only the port if you need to.
- **A lesson's printed output doesn't match this course's example
  output exactly**: for lessons that call an AI model, that's expected,
  the model's wording varies between runs. What should stay the same is
  the *shape* of the output (how many lines, what's labeled what); the
  exact sentence won't be identical every time.

## Getting help

Several lesson checkpoints suggest asking a question before moving on
if something's still unclear. For this repo, that means opening a
[GitHub Issue](../../issues) with the lesson number and what's
confusing, rather than a live forum or chat.

---

Built by Andrei Nita — [andreinita.co](https://andreinita.co)
