# Lesson 18: Intermediate Checkpoint - Notes Search Assistant with Citations

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built entirely out of ideas from Lessons 10 through 17, combined
into one thing. If you can read `lesson.py` and understand why every
piece is there, you've mastered the Intermediate tier. If any piece
feels unfamiliar, that's a sign to revisit the lesson it came from
before continuing to Advanced.

## What it does

Loads (or builds and persists) an embedding index over every fixture
note, then answers two questions: one that needs two different sources
combined with citations, and one with no relevant information at all,
demonstrating retrieval's threshold correctly refusing to answer instead
of guessing.

## Where each piece came from

```python
def load_or_build_store() -> list[dict]:
    if STORE_PATH.exists():
        return json.loads(STORE_PATH.read_text())
    store = build_vector_store()
    STORE_PATH.write_text(json.dumps(store))
    return store
```
Lesson 13 (persistence): build and save once, load on every run after
that, no repeated embedding calls.

```python
return [
    {"text": text, "embedding": vector, "source": path.name}
    for path, text, vector in zip(paths, texts, vectors)
]
```
Lesson 12 (metadata): every record carries its source filename.

```python
above_threshold = [record for record in scored if record["score"] >= min_score]
return above_threshold[:k]
```
Lesson 14 (thresholds): retrieval can honestly return nothing when
nothing clears `MIN_SCORE`, instead of always returning `k` results.

```python
if not retrieved_chunks:
    return "I don't have any information relevant to that question."
```
Lesson 15 (grounded prompting): skip the API call entirely when there's
nothing relevant to answer from.

```python
context = "\n\n".join(
    f"[Source: {chunk['source']}]\n{chunk['text']}" for chunk in retrieved_chunks
)
```
Lesson 15 (citations): each chunk is tagged with its source before being
handed to the model, so the model can cite it.

(Lessons 10, 11, 16, and 17's chunking, structure, and evaluation
lessons don't appear directly in this script's code, since this
checkpoint indexes whole fixture files the same way Lesson 9's did, but
everything they taught about *why* those choices matter is what this
script's design decisions rest on.)

## Running it

```bash
uv run python lessons/naive_rag/02_intermediate/18_intermediate_checkpoint_project/lesson.py
```

You should see: the pizza question answered by combining `pizza-dough.md`
(the cold ferment time, and that the basil comes from "the garden's
tomato bed") with `garden.md` (that the tomato bed specifically is "the
first bed"), each fact cited to its actual source, and the France
question correctly refused without an extra API call.

## Try this yourself

Without looking anything up:

- Delete `store.json` and rerun, confirm it re-embeds and rebuilds
  correctly.
- Lower `MIN_SCORE` to `0.3` and rerun the France question, does it now
  retrieve an irrelevant chunk and try to answer anyway?
- Add a new fixture `.md` file, delete `store.json`, and ask a question
  only that new file can answer, does it get indexed and cited
  correctly on the next run?

If you can make these changes confidently, you're ready for the
Advanced tier, starting at Lesson 19.
