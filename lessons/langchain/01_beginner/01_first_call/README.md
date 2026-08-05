# Lesson 1: Send a message to an AI, get an answer back

## What we're building

A tiny program that sends one question to an AI (Google's Gemini) and
prints its answer. No tricks yet, this is the starting point everything
else in this project builds on.

## API keys: proving who you are

AI companies run their models on their own expensive servers, and they
need to control who's allowed to use them (partly for security, partly
so they can track usage and enforce free-tier limits). The way they do
that is with an **API key**: a long secret string, kind of like a
password, that you send along with every request. Their server checks
the key, confirms it's valid, and only then processes your request.

We keep our key in a file called `.env`, in the project's root folder.
We never type the key directly into our Python files, and we never share
that file, because anyone holding the key could use it as if they were
us, spending our free-tier quota or, if we were on a paid plan, our
money.

## What LangChain actually does

Every AI company (Google, OpenAI, Anthropic, and others) has its own way
of formatting requests and responses. If you wrote code directly against
Google's API, switching to a different AI later would mean rewriting a
lot of that code.

LangChain is a library that sits between your code and all of these
different AI providers. You write code once, using LangChain's
consistent interface, and LangChain translates it into whatever format
each specific provider needs underneath. Swapping providers later
usually means changing one or two lines, not your whole program.

## The code, piece by piece

```python
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
```

These `import` lines pull in code that other people already wrote and
published, so we don't have to write it ourselves. `load_dotenv` knows
how to read a `.env` file. `ChatGoogleGenerativeAI` is LangChain's class
for talking specifically to Google's Gemini models.

```python
load_dotenv()
```

Runs the function we imported: reads `.env`, and makes `GOOGLE_API_KEY`
available to the rest of the program (technically, it loads it as an
environment variable, a value the operating system keeps track of for
the current program run).

```python
model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
```

This creates an object, `model`, that represents a connection to one
specific AI. `"gemini-3.5-flash-lite"` is that model's name. "Flash"
versions are built to respond quickly and are cheap or free to use, in
exchange for being slightly less powerful than the biggest, slowest
models. "Lite" is the smallest Flash variant, which also means it gets
the highest free-tier request limit, useful while we're calling it
repeatedly to learn.

At this point, no message has actually been sent yet, we've only set up
the connection.

```python
response = model.invoke("In one sentence, what is LangChain for?")
```

`.invoke()` is the method that actually sends something and waits for a
reply. This is a **blocking call**: your program pauses on this line
until the answer comes back over the network, could be under a second,
could be a few seconds.

The thing that comes back, `response`, isn't plain text. It's an object
(LangChain calls it an `AIMessage`) that bundles the AI's written reply
together with extra metadata: which model answered, how many tokens
(roughly, word-pieces) were used, and more.

```python
print(response.text)
```

`.text` pulls just the written answer out of that bundle, ignoring the
metadata, so we can print something readable.

## Running it

```bash
uv run python lessons/langchain/01_beginner/01_first_call/lesson.py
```

## Expected output

A single sentence printed to the terminal, something like:

```
LangChain is a framework for building applications powered by large language models.
```

The exact wording will differ every time you run it, that's the AI
answering freely, not a bug. If instead you see an error, check the
[Troubleshooting section](../../../../README.md#troubleshooting) in
this project's root README.

## Checkpoint

- **API key**: a secret credential sent with each request to prove who's
  asking.
- **model** (the object): your program's connection to one specific AI.
- **`.invoke()`**: send input, block until a reply comes back.
- **LangChain**: a shared interface across many different AI providers,
  so switching providers doesn't mean rewriting everything.

If anything here still feels unclear, ask before moving to Lesson 2.
