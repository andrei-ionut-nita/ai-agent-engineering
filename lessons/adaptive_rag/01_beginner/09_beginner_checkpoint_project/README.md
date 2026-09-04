# Lesson 9: Beginner Checkpoint - CLI Q&A That Routes Automatically

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built entirely out of ideas from Lessons 1 through 8, combined
into one thing. If you can read `lesson.py` and understand why every
piece is there, you've mastered the Beginner tier. If any piece feels
unfamiliar, that's a sign to revisit the lesson it came from before
continuing to Intermediate.

## What it does

Loads every fixture note in `lessons/adaptive_rag/fixtures/notes/` (the
same five short files this whole course has used, a weather station, a
garden, a pizza recipe, a bookshelf, and cello practice), embeds and
stores all of them, then answers four questions, one of each label this
tier classifies into (plus one repeat) and prints which strategy handled
each one before printing its answer, so you can watch the router make a
different decision per question in one run.

## Where each piece came from

```python
def load_documents() -> list[dict]:
    paths = sorted(NOTES_DIR.glob("*.md"))
    return [{"text": path.read_text(), "source": path.name} for path in paths]
```
`naive_rag` Lesson 9's twist on chunking, unchanged: each short fixture
file is already one chunk, no splitting needed. `sorted(...)` keeps file
order consistent across runs.

```python
store = build_vector_store(documents)
```
Lesson 4 (itself `naive_rag` Lesson 5's shape), unchanged: embed every
document in one batched call, pair each with its embedding.

```python
classification = classify(query)
```
Lesson 3: a structured, `response_schema`-constrained call that labels
a question `simple_factual`, `multi_hop`, or `ambiguous`, with a
one-sentence reason.

```python
STRATEGIES: dict[str, Callable[[str, list[dict]], str]] = {
    "simple_factual": answer_simple,
    "multi_hop": answer_multi_hop,
    "ambiguous": answer_ambiguous,
}
```
Lesson 5's reusable dispatch shape, extended to three entries by Lesson
6: `answer_simple` is naive top-1 retrieval (Lesson 4), `answer_multi_hop`
retrieves across the whole corpus and lets Gemini synthesize (Lesson 4),
`answer_ambiguous` retrieves narrow, grades, and only broadens if the
grade says the narrow attempt fell short (Lesson 6).

```python
def answer(query: str, store: list[dict]) -> dict:
    classification = classify(query)
    strategy = STRATEGIES[classification.label]
    result = strategy(query, store)
    return {"question": query, "label": classification.label, "answer": result}
```
Lesson 8's whole pipeline, unchanged: classify, route, return both the
label and the answer.

## Running it

```bash
uv run python lessons/adaptive_rag/01_beginner/09_beginner_checkpoint_project/lesson.py
```

You should see: a wind-sensor question routed to `simple_factual`, a
same-room-hobbies question routed to `multi_hop` and correctly naming
both hobbies, a wind-speed question routed to `ambiguous` and correctly
combining a detail from `weather-station.md` with one from `garden.md`,
and a pizza-oven question routed back to `simple_factual`, each one
handled by a different strategy chosen automatically from the question
alone, no strategy named by hand anywhere in the question list.

## Try this yourself

Without looking anything up:

- Ask a question this course's fixtures genuinely can't answer (try
  "What is the capital of France?", the same out-of-corpus question
  `naive_rag` and `corrective_rag` both used). Which label does it get,
  and does that route's answer honestly admit the notes don't cover it,
  or does it guess?
- Change `answer_ambiguous`'s narrow retrieval from `k=1` to `k=2` before
  grading. Does the grading step still trigger a broaden-and-retry as
  often, or does the wider first pass already look sufficient more of
  the time?
- Add a new `.md` file of your own to `fixtures/notes/` (a made-up note
  about a topic not already covered) and ask a question that spans it
  and one existing file. Does the classifier label it `multi_hop`
  correctly, and does `answer_multi_hop` actually pull in your new file?

If you can make these changes confidently, you're ready for the
Intermediate tier, starting at Lesson 10.
