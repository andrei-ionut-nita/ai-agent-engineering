# Lesson 15: Prompting for Grounded Answers

## Where we left off

Lesson 7's prompt already told Gemini to answer "using only the context"
and to admit when it doesn't know. Lesson 14 added a threshold so
retrieval can return nothing at all when nothing is relevant. This
lesson connects the two, and adds one more thing neither lesson had:
telling the reader *which* source backs each claim, not just trusting
the answer is grounded.

## Two small, deliberate upgrades

**No wasted API call.** If retrieval (with Lesson 14's threshold) comes
back empty, there's no reason to ask Gemini anything, the honest answer
is already known. Checking for that up front:

```python
if not retrieved_chunks:
    return "I don't have any information relevant to that question."
```

**Citations, not just grounding.** Lesson 7's prompt kept the model
honest about *whether* it knew something; it never asked the model to
say *where* an answer came from. Tagging each chunk with its source
before building the prompt, and instructing the model to cite it, closes
that gap:

```python
context = "\n\n".join(
    f"[Source: {chunk['source']}]\n{chunk['text']}" for chunk in retrieved_chunks
)
```

```
- Every claim in your answer must cite which source it came from, like this: (according to garden.md).
```

## The code, piece by piece

```python
prompt = f"""Answer the question using only the context below.

Rules:
- If the context doesn't contain the answer, say "I don't have information about that."
- Every claim in your answer must cite which source it came from, like this: (according to garden.md).
- Do not use any knowledge you have that isn't in the context below.
"""
```

Spelling the rules out as a numbered list, rather than one folded-in
sentence like Lesson 7's version, makes each requirement unambiguous on
its own. This matters more as a prompt does more work: "use only the
context," "admit not knowing," and "cite sources" are three separate
instructions, and a model is more likely to follow all three when
they're not competing for attention inside one sentence.

## Running it

```bash
uv run python lessons/naive_rag/02_intermediate/15_prompting_for_grounded_answers/lesson.py
```

## Expected output

```
Q: Where does the basil topping on the pizza come from, and how is the garden watered?
A: The basil topping on the pizza comes from the garden's tomato bed (according to pizza-dough.md).

The garden is watered early in the morning, before the sun is high, so
less water is lost to evaporation (according to garden.md). Specifically,
the tomato bed is watered daily in the summer, while the root vegetable
bed is watered every two or three days (according to garden.md).

Q: What is the capital of France?
A: I don't have any information relevant to that question.
```

The first question needs two sources at once (`pizza-dough.md` and
`garden.md`), and the answer cites both correctly. The second question
never reaches Gemini at all, no relevant chunk clears Lesson 14's
threshold, so the fixed fallback message is returned directly.

## Checkpoint

- **citations**: tagging each chunk with its source and instructing the
  model to reference it, so an answer's grounding is checkable, not just
  claimed.
- **skip the call when there's nothing to retrieve**: an empty retrieval
  result is itself an answer ("I don't know"), not a reason to ask the
  model anyway.
- Numbered, explicit rules in a prompt tend to all get followed more
  reliably than the same requirements folded into one sentence.

If anything here still feels unclear, ask before moving to Lesson 16.
