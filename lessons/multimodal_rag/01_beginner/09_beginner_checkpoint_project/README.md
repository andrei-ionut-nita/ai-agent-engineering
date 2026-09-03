# Lesson 9: Beginner Checkpoint - CLI Q&A Over Notes and Images

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built entirely out of ideas from Lessons 1 through 8, combined
into one thing. If you can read `lesson.py` and understand why every
piece is there, you've mastered the Beginner tier. If any piece feels
unfamiliar, that's a sign to revisit the lesson it came from before
continuing to Intermediate.

## What it does

Builds the mixed store (Lesson 6: five notes, four images captioned and
embedded), then answers four questions, one answerable only from a
note's text, one answerable only from an image, and two spanning
different notes and images, printing the whole run so you can see
retrieval pick the right modality for each question without being told
which modality to use.

## Where each piece came from

```python
def build_mixed_store() -> list[dict]:
    ...
```
Lesson 6, unchanged: text records from `fixtures/notes/`, image records
from `fixtures/images/` (captioned via Lesson 4's `caption_image`,
embedded via Lesson 5's `embed_texts`), concatenated into one list.

```python
def retrieve(query: str, store: list[dict], k: int) -> list[dict]:
    ...
```
Lesson 7, unchanged: the same `retrieve()` `naive_rag` has used since
its own Lesson 6, run here against a store that happens to contain
captions as well as document chunks.

```python
def generate_answer(query: str, retrieved: list[dict]) -> str:
    ...
```
Lesson 8, unchanged: build `contents` record by record, re-attaching a
retrieved image's *original file*, or a retrieved chunk's text, then
generate.

```python
def ask(query: str, store: list[dict], k: int = 2) -> str:
    retrieved = retrieve(query, store, k)
    return generate_answer(query, retrieved)
```
The whole pipeline as one function call, the same shape `naive_rag`
Lesson 8 introduced, now running over text and images without any
branch in `ask()` itself, the branching happens once, inside
`generate_answer`.

## Running it

```bash
uv run python lessons/multimodal_rag/01_beginner/09_beginner_checkpoint_project/lesson.py
```

You should see: a bike maintenance question answered from
`bike-repair.md`'s text, a torque-spec question answered by looking at
`derailleur-hanger-diagram.png` directly, a starter-feeding question
combining `sourdough-starter.md`'s text with `starter-jar-markings.png`,
and an observatory-motor-wiring question answered from
`observatory-mount-wiring.png`, each retrieved from the correct modality
with no hint in the question about which one to search.

## Try this yourself

Without looking anything up:

- Ask a question about `terrarium.md` or `circuit-board.md` (the two
  fixture notes with no matching image). Does retrieval correctly stay
  text-only for those, with no image ever attached at generation time?
- Change `k` from 2 to 1 on the sourdough question. Does it still
  retrieve enough of the right modality mix to answer correctly, or
  does it now only get the text half (or only the image half) of the
  answer?
- Write your own question whose answer needs `observatory-finder-scope.png`
  specifically (not the wiring image), does it retrieve the correct one
  of the two `home-observatory.md` figures?

If you can make these changes confidently, you're ready for the
Intermediate tier, starting at Lesson 10.
