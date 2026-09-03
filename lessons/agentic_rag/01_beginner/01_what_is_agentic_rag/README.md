# Lesson 1: What Is Agentic RAG, and Why Let the Model Decide?

## Where we left off

If you've done any of this repo's other RAG courses (or read
[andreinita.co/learning/rag-fundamentals](https://andreinita.co/learning/rag-fundamentals/)),
every one of them shares an assumption baked in at the pipeline level:
a question comes in, retrieval runs, then generation runs. Always, no
exceptions, regardless of whether the question actually needed a
document at all.

**Agentic RAG** removes that assumption. Instead of a fixed
retrieve-then-generate pipeline, the model itself is given retrieval as
one *tool* among possibly several, and it decides, per question,
whether to call it, how many times, and what else it might call
instead. This course builds that decision-making loop from scratch,
using Gemini's native function calling, no framework in between.

## The misconception this lesson corrects

It's tempting to assume "agentic" just means "the same RAG pipeline,
but with an LLM wrapper around it." It doesn't. The actual shift is
narrower and more concrete: **retrieval stops being a step the pipeline
always runs, and becomes a function the model can choose to invoke, or
not, based on the specific question in front of it.** A question the
model can already answer correctly doesn't need retrieval at all, and
forcing it through the old fixed pipeline anyway is pure waste, an
embedding call and a similarity search that changed nothing about the
final answer.

## The code, piece by piece

```python
response = client.models.generate_content(model=CHAT_MODEL, contents=GENERAL_QUESTION)
```

Same raw `google-genai` call every course in this series uses,
[naive_rag Lesson 1](../../../naive_rag/01_beginner/01_what_is_naive_rag/README.md)'s
`client.models.generate_content()`. No tools declared yet, that starts
in Lesson 3.

This lesson asks Gemini two questions back to back: one it can answer
correctly from training alone (water's boiling point), and one whose
real answer lives only in this course's `fixtures/notes/sourdough-starter.md`,
a file it has never seen. The point isn't the second question failing,
every course in this series has already shown that failure. The point
is the *first* question succeeding, with zero retrieval, which a fixed
pipeline would never have allowed, it retrieves unconditionally for
both.

## Running it

```bash
uv run python lessons/agentic_rag/01_beginner/01_what_is_agentic_rag/lesson.py
```

## Expected output

Gemini's exact wording varies, but the shape is consistent: a correct
answer to the boiling-point question, and either an "I don't know" or a
wrong guess on the sourdough question, followed by this course's
framing of the difference.

## Checkpoint

- **Agentic RAG**: retrieval as a tool the model chooses to call, not a
  pipeline step that always runs.
- The core shift is about *when* retrieval happens, not about adding
  more LLM calls around the same fixed pipeline.
- A question answerable from the model's own training gets no benefit
  from forced retrieval, and pays a real cost (an extra embedding call,
  extra latency) for it.
- Lesson 2 makes the old, always-retrieve pipeline concrete and running,
  so Lesson 3 onward has something specific to replace.

If anything here still feels unclear, ask before moving to Lesson 2.
