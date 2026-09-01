# Lesson 9: Beginner Checkpoint - CLI Q&A Assistant

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built entirely out of ideas from Lessons 1 through 8, combined
into one thing. If you can read `lesson.py` and understand why every
piece is there, you've mastered the Beginner tier. If any piece feels
unfamiliar, that's a sign to revisit the lesson it came from before
continuing to Intermediate.

## What it does

Loads every fixture note in `lessons/naive_rag/fixtures/notes/` (five
short Markdown files about a weather station, a garden, a pizza recipe,
a bookshelf, and cello practice), embeds and stores all of them, then
answers three questions, each one drawing on a different file, printing
the whole run so you can see the pipeline work across more than one
document for the first time.

## Where each piece came from

```python
def load_documents() -> list[str]:
    return [path.read_text() for path in sorted(NOTES_DIR.glob("*.md"))]
```
A new twist on Lesson 4's chunking, not a new concept: instead of
splitting one long file into chunks, each already-short file *is* one
chunk. `sorted(...)` keeps the file order consistent across runs
(`glob` alone doesn't guarantee an order).

```python
store = build_vector_store(documents)
```
Lesson 5, unchanged: embed every chunk in one batched call, pair each
with its embedding.

```python
retrieved = retrieve(query, store, k)
```
Lesson 6, unchanged: embed the question, rank every chunk by cosine
similarity, keep the top `k`.

```python
return generate_answer(query, retrieved)
```
Lesson 7, unchanged: stuff the retrieved chunks into a prompt, ask
Gemini to answer only from that context.

```python
def ask(query: str, store: list[dict], k: int = 2) -> str:
    retrieved = retrieve(query, store, k)
    return generate_answer(query, retrieved)
```
Lesson 8's `ask()`, unchanged: the whole pipeline as one function call.

## Running it

```bash
uv run python lessons/naive_rag/01_beginner/09_beginner_checkpoint_project/lesson.py
```

You should see: a wind-sensor question answered from
`weather-station.md`, a cello question answered from
`cello-practice.md`, and a basil-topping question answered by combining
a detail from `pizza-dough.md` with `garden.md` (both mention basil),
each pulled correctly out of five short, unrelated-sounding documents
with no keyword overlap forcing the match.

## Try this yourself

Without looking anything up:

- Add a new `.md` file of your own to `fixtures/notes/` (a made-up note
  about a topic not already covered), does asking about it work
  correctly on the next run?
- Change `k` from 2 to 1 in one of the `ask()` calls, does the pizza
  question (which needs the recipe file specifically) still get
  answered correctly with only the single best match?
- Ask a question that spans two files at once, for example "What two
  hobbies happen in the same room as the weather station?" (the answer
  needs `bookshelf.md` and `cello-practice.md` together). Does `k=2`
  retrieve both of the right files, or does it miss one?

If you can make these changes confidently, you're ready for the
Intermediate tier, starting at Lesson 10.
