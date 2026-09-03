# Lesson 2: The Fixed-Pipeline Assumption, Made Concrete

## Where we left off

Lesson 1 showed the problem in words: a fixed pipeline retrieves
unconditionally, even for questions that don't need it. This lesson
builds that fixed pipeline for real, the exact shape
[naive_rag](../../../naive_rag/README.md) through
[corrective_rag](../../../corrective_rag/README.md) all share, embed
every fixture note, retrieve the top `k` for whatever question arrives,
stuff it into the prompt, generate, then runs it against both of
Lesson 1's questions to watch the waste happen directly instead of
just being told about it.

## The code, piece by piece

```python
def fixed_pipeline_ask(query: str, store: list[dict]) -> str:
    retrieved = retrieve(query, store)
    ...
```

Nothing here is new, it's [naive_rag Lesson 8](../../../naive_rag/01_beginner/08_end_to_end_single_document_qa/README.md)'s
whole pipeline in one function, unchanged. The only thing this lesson
adds is calling it on a question, the boiling-point one, where
retrieval was never necessary, and watching what happens anyway: an
embedding call for the query, a similarity search across every note,
and a prompt stuffed with the closest-matching (but still irrelevant)
fixture content, all before Gemini ever gets asked anything.

## Why this matters

Gemini usually still answers the boiling-point question correctly,
it's common enough knowledge that a few irrelevant paragraphs about a
sourdough starter or a pedalboard don't derail it. But "usually still
gets it right despite the noise" is not the same as "the noise was
free." Every fixed-pipeline call pays for an embedding request and a
similarity search regardless of whether the question needed either,
and on a harder or more ambiguous general-knowledge question,
irrelevant retrieved context can actively pull the model toward a wrong
answer instead of a right one, not just waste time getting to a right
one.

## Running it

```bash
uv run python lessons/agentic_rag/01_beginner/02_the_fixed_pipeline_assumption/lesson.py
```

## Expected output

```
Q: What temperature does water boil at, at sea level, in Celsius?
A: <a correct answer, likely mentioning 100°C, despite irrelevant retrieved context>

Q: How often does Clarence the sourdough starter need feeding at room temperature?
A: <a grounded answer, "every 12 hours">
```

## Checkpoint

- The fixed pipeline (retrieve, then generate) has no way to ask "does
  this question actually need retrieval?", it always retrieves.
- That costs an embedding call and a similarity search on every single
  question, whether or not either one changes the final answer.
- Lesson 1's boiling-point question and this lesson's sourdough
  question paid the identical cost for very different value: none, and
  everything, respectively.
- Fixing this requires the model itself to have a way to decide,
  question by question, whether to retrieve. That mechanism, Gemini's
  native function calling, is Lesson 3.

If anything here still feels unclear, ask before moving to Lesson 3.
