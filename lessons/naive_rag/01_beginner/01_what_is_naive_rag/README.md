# Lesson 1: What Is Naive RAG, and Why Build It by Hand First?

## Where we left off

If you've read [andreinita.co/learning/rag-fundamentals](https://andreinita.co/learning/rag-fundamentals/)
(or this repo's other courses' RAG lessons), you've already met the idea
of retrieval-augmented generation in prose: an AI model only knows what
it was trained on, so RAG hands it fresh, relevant text at the moment
it's asked a question, instead of retraining it. This course builds that
idea, literally, starting from nothing.

**Naive (Standard) RAG** is the baseline version of that idea: chunk a
document into passages, embed them, retrieve the ones closest in meaning
to the question, and stuff them into the prompt. Every other RAG
architecture in the wider taxonomy (Hybrid, Graph, Corrective, Agentic,
and so on) is a variation or extension of this exact four-stage shape,
so this course is the foundation the rest of the series builds on.

## Why build it by hand, with no framework?

This repo's `langchain`, `llamaindex`, and `pgvector` courses already
teach RAG *through* a framework or database, where a lot of the four
stages above happen inside one method call. That's the right way to
build a real system, but it can leave the actual mechanics a little
opaque: what is `embed_documents` really doing? What does "similarity"
mean as a number?

This course answers those questions directly: no `LangChain`, no
`LlamaIndex`, just `google-genai` (Gemini's own official Python SDK) and
a plain Python list standing in for a vector database. By the time you
reach this course's Advanced tier and reintroduce a real vector library
(`chromadb`), you'll know exactly what it's doing for you, because
you'll have already done it yourself.

## The code, piece by piece

```python
from google import genai
client = genai.Client()
```

`google-genai` is Google's own SDK for Gemini, the same one LangChain's
`ChatGoogleGenerativeAI` and LlamaIndex's `GoogleGenAI` classes use
underneath. `genai.Client()` reads `GOOGLE_API_KEY` from your environment
automatically (that's why `load_dotenv()` runs first) and gives you one
object, `client`, through which every Gemini call in this course goes.

```python
response = client.models.generate_content(model=CHAT_MODEL, contents=QUESTION)
```

`generate_content` is the raw-SDK equivalent of `.invoke()`: send some
text, block until Gemini replies. `response.text` (used below) pulls out
just the written answer, same idea as LangChain's `AIMessage.text`.

The question this lesson asks is answered inside this course's own
`fixtures/notes/weather-station.md` file, a file Gemini has never seen.
Run it and Gemini will either admit it doesn't know, or, as often
happens, invent a specific-sounding but wrong answer. Both outcomes are
the same underlying problem: the model can only answer from what it was
trained on, and a small personal note about a Raspberry Pi weather
station was never part of that training data.

## Running it

```bash
uv run python lessons/naive_rag/01_beginner/01_what_is_naive_rag/lesson.py
```

## Expected output

Gemini's actual wording varies every run, but the shape is consistent:
either an admission it doesn't have this information, or a confident,
invented answer, followed by this course's four-stage roadmap:

```
Question: How often does Project Aurora's wind speed sensor need re-oiling?

Gemini, with no context:
<a guess, or an "I don't know" - varies each run>

Naive RAG's four stages, built one at a time starting next lesson:
  1. Chunk    - split a document into small, retrievable passages
  2. Embed    - turn each passage (and the question) into a vector
  3. Retrieve - find the passages whose vectors are closest to the question's
  4. Generate - hand those passages to Gemini alongside the question
```

If instead you see an error, check the
[Troubleshooting section](../../../../README.md#troubleshooting) in
this project's root README.

## Checkpoint

- **Naive RAG**: chunk, embed, retrieve, generate - the baseline
  architecture every other RAG variant builds on.
- **`google-genai`**: Gemini's own SDK, used directly in this course
  instead of through LangChain or LlamaIndex.
- **`client.models.generate_content()`**: the raw-SDK call that sends a
  prompt and blocks for a reply.
- **Why RAG exists**: a model can't answer from documents it was never
  trained on, no matter how the question is worded.

If anything here still feels unclear, ask before moving to Lesson 2.
