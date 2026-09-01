# Lesson 8: End to End, Single-Document Q&A

## What we're building

One function, `ask()`, that wires together everything from Lessons 4
through 7: chunk a document, build a vector store, retrieve the most
relevant chunks for a question, and generate a grounded answer. This is
Naive RAG's complete four-stage pipeline, in nine lines, running against
three different questions to show what it handles well and what it
doesn't.

## The whole pipeline, in one function

```python
def ask(query: str, store: list[dict], k: int = 2) -> str:
    retrieved = retrieve(query, store, k)
    return generate_answer(query, retrieved)
```

That's genuinely the entire "Naive RAG" architecture, once chunking and
embedding have already happened once to build `store`. Everything this
course covers from here forward, better chunking, persistence,
thresholds, a real vector database, is refinement around this same
two-line shape, not a replacement for it.

## Three questions, three outcomes

This lesson asks `ask()` three different questions on purpose:

1. *"What's the best way to get a crispy pizza crust?"* - directly
   answerable from one chunk, the easy case Lessons 6-7 already proved
   works.
2. *"How does the household decide what to plant in the third garden
   bed?"* - also answerable, but notice the chunk says the bed "rotates
   whatever seeds are left over," a much vaguer answer than the pizza
   question got. Retrieval found the right chunk; the chunk itself just
   doesn't contain a detailed answer.
3. *"What is the capital of France?"* - not in the document at all. A
   good outcome here is Gemini saying the context doesn't contain the
   answer, per Lesson 7's prompt instruction. If it answers "Paris"
   anyway, using outside knowledge instead of admitting the context
   doesn't cover it, that's a preview of a failure mode Lesson 16 covers
   properly: retrieval still returns its top-`k` chunks *even when
   none of them are actually relevant*, since "most similar" isn't the
   same guarantee as "similar enough to be useful."

## Running it

```bash
uv run python lessons/naive_rag/01_beginner/08_end_to_end_single_document_qa/lesson.py
```

## Expected output

```
Q: What's the best way to get a crispy pizza crust?
A: <grounded answer about 00 flour, cold ferment, preheated steel>

Q: How does the household decide what to plant in the third garden bed?
A: <a vaguer answer, matching how vague the source chunk itself is>

Q: What is the capital of France?
A: <ideally, an admission the context doesn't contain this>
```

If the third answer confidently says "Paris" instead of admitting the
context doesn't cover it, that's not a bug in your code, it's a real,
common Naive RAG failure mode you'll fix properly in Lesson 14
(similarity thresholds) and Lesson 15 (tighter grounding instructions).

## Checkpoint

- **the full pipeline**: `retrieve()` then `generate_answer()`, two
  function calls, is the entire Naive RAG architecture once a vector
  store exists.
- Retrieval always returns its top-`k` chunks, even if none of them are
  actually relevant, "most similar of what's available" isn't the same
  as "good enough to answer with."
- This is the version of Naive RAG the rest of this course tunes and
  hardens, not a toy that gets thrown away.

If anything here still feels unclear, ask before moving to Lesson 9.
