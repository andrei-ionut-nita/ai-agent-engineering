# Lesson 1: What is Ollama?

## Cloud models vs local models

Every other course in this repo sends your request to Google over the
internet: `ChatGoogleGenerativeAI(model=...)`, `.invoke()`, and the
answer comes back from a server Google owns and runs. That's the
normal way most people build with AI, and it's a great default: you
get access to huge, extremely capable models without owning any
special hardware.

Ollama flips that. It downloads a model's weights (the actual numbers
that make the model work, gigabytes of them) onto your own machine,
then runs the model there, using your own CPU or GPU. Your program
still talks to it over HTTP, exactly like it talks to Gemini, but the
other end of that connection is `localhost`, not Google's data
centers.

| | Cloud (Gemini) | Local (Ollama) |
|---|---|---|
| Where it runs | Google's servers | Your machine |
| Needs network | Every single call | Only to download the model, once |
| Cost | Free tier, then per-token | Free, limited only by your hardware |
| Privacy | Your prompts leave your machine | Your prompts never leave it |
| Quality ceiling | Very high | Lower, bounded by what your machine can run |
| Speed | Depends on network and provider load | Depends entirely on your hardware |

Neither side is strictly better, they're a tradeoff. This course
teaches the local side: when to reach for it (cost, privacy, offline
work, experimentation without burning API quota) and its real limits
(a laptop can't run the biggest models, and there's no free lunch on
speed if your hardware is modest).

## How Ollama actually works

Ollama itself is not a Python package, it's an application (like
Postgres or Docker) that runs in the background on your machine and
exposes an HTTP API on `http://localhost:11434`. The `ollama` Python
package this lesson imports is just a thin client for that local API,
the same relationship `psycopg` has to a running Postgres server in
the pgvector course.

That means two separate things had to happen before this lesson's code
could work, both covered in this course's [README](../../README.md):

1. **Install the Ollama application** itself, a one-time download from
   [ollama.com/download](https://ollama.com/download). It starts a
   background service the moment it's installed.
2. **Pull a model**: `ollama pull llama3.2`. "Pulling" downloads that
   model's weights from Ollama's library to your machine, the same
   idea as `docker pull` for a container image. This only needs to
   happen once per model; after that, it's stored on disk.

## The code, piece by piece

```python
import ollama
```

The Python client. Unlike `ChatGoogleGenerativeAI`, there's no API key
to load, because there's no remote provider to authenticate against.

```python
response = ollama.list()
```

Asks the local Ollama server which models are already pulled. This is
a real network call, just to `localhost` instead of the public
internet, which is why the lesson wraps it in a `try`/`except`: if the
Ollama application isn't running, this call fails with a
`ConnectionError`, not an API-key error like the Gemini lessons.

```python
for model in response.models:
    size_gb = model.size / 1_000_000_000
    print(f"  {model.model} ({size_gb:.1f} GB, {model.details.parameter_size} params)")
```

`response.models` is a list of `Model` objects, one per pulled model,
each with a name (`.model`), a size in bytes, and `.details`, which
includes the parameter count and quantization level (more on
quantization in Lesson 18).

## Running it

```bash
uv run python lessons/ollama/01_beginner/01_what_is_ollama/lesson.py
```

## Expected output

The comparison table is fixed text, but the model list depends on
what you've pulled. If you followed this course's setup and pulled
`llama3.2`, you'll see at least that:

```
Cloud (Gemini, every other course) vs local (Ollama, this course):
  Where the model runs: Google's servers (cloud) vs your machine (local)
  Network required: Yes, every call vs no, after the model is downloaded
  Cost: Free tier, then per-token vs free, limited only by your hardware
  Privacy: Your prompts leave your machine vs your prompts never leave it
  Quality ceiling: Very high (huge models) vs lower (bounded by your RAM/GPU)
  Speed: Depends on network + provider load vs depends on your hardware

Models already pulled on this machine:
  llama3.2:latest (2.0 GB, 3.2B params)
```

If you see a connection error instead, the Ollama application isn't
running, see this course's [README](../../README.md) or this project's
root [Troubleshooting section](../../../../README.md#troubleshooting).

## Checkpoint

- **Ollama**: a background application that runs LLMs on your own
  machine and serves them over a local HTTP API.
- **Pulling a model**: a one-time download of that model's weights to
  your disk, like `docker pull` for a container image.
- **The `ollama` Python package**: a thin client for the local API, no
  API key involved, because there's no remote provider.
- **Cloud vs local**: a tradeoff between quality ceiling and
  cost/privacy/offline capability, not a strictly-better-or-worse
  choice.

If anything here still feels unclear, ask before moving to Lesson 2.
