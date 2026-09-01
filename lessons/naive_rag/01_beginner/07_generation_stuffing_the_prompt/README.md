# Lesson 7: Generation, Stuffing the Prompt

## What we're building

A function that takes the chunks Lesson 6's retrieval returned and hands
them to Gemini, alongside the original question, so the answer is
grounded in that specific text instead of whatever Gemini happened to
learn during training. This is "generation," the fourth and final stage
of Naive RAG.

## "Stuffing" is a real, if inelegant, name

The technique here doesn't have a more sophisticated name because there
isn't a more sophisticated technique yet at this point in the course:
you take the retrieved text, and you literally paste it into the prompt,
ahead of the question. Gemini has no separate channel for "trusted
background information," from its point of view, the context and the
question are just one long piece of text it's asked to respond to.

That simplicity is exactly why this is called *Naive* RAG. Later
lessons in this series (Corrective RAG, Agentic RAG) add steps like
grading the retrieved text before using it, or deciding whether to
retrieve again, but the core move, put the text in the prompt, stays the
same underneath all of them.

## The code, piece by piece

```python
context = "\n\n---\n\n".join(chunk["text"] for chunk in retrieved_chunks)
```

Joins every retrieved chunk's text into one block, with a clear `---`
separator between them. Without a separator, two adjacent chunks could
visually run together and confuse the model about where one topic ends
and the next begins.

```python
prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {query}"""
```

The instruction ("using only the context... don't guess") matters more
than it might look. Without it, Gemini will happily blend the retrieved
context with whatever it already "knows" from training, which defeats
the purpose: you want an answer grounded in *this* document, not a
plausible-sounding mixture of this document and outside knowledge.
Lesson 15 comes back to this instruction and tightens it further.

```python
response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
return response.text or ""
```

The same `generate_content` call from Lesson 1, just with a longer,
more structured prompt this time. `or ""` guards against the rare case
where `.text` comes back empty (a fully blocked or filtered response),
so the function's return type stays a plain string either way.

## Running it

```bash
uv run python lessons/naive_rag/01_beginner/07_generation_stuffing_the_prompt/lesson.py
```

## Expected output

```
Question: What's the best way to get a crispy pizza crust?

Answer:
<an answer describing 00 flour, a 48-hour cold ferment, baking at the
highest oven setting with a preheated steel - the specific details from
the retrieved chunk, not a generic answer>
```

Compare this to Lesson 1's version of asking Gemini something it doesn't
know: the difference is retrieval handing it the right text first.

## Checkpoint

- **generation**: handing retrieved text to the model alongside the
  question, so the answer is grounded in that specific text.
- **"stuffing"**: pasting retrieved text directly into the prompt, the
  simplest possible way to give a model context, and Naive RAG's
  namesake technique.
- The instruction to answer "using only the context" is doing real
  work, without it the model blends retrieved text with its own
  training knowledge.

If anything here still feels unclear, ask before moving to Lesson 8.
