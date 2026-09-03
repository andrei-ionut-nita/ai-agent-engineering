# Lesson 2: The Blind Spot of Text-Only Retrieval

## Where we left off

Lesson 1 asked Gemini a question with *no* context at all and, unsurprisingly,
it couldn't answer. A natural response is "fine, so build real RAG": chunk
`fixtures/notes/`, embed the chunks, retrieve the best match, generate from
it, exactly `naive_rag`'s pipeline. This lesson builds exactly that, unchanged
from `naive_rag`, and shows it *still* fails on the same question. That's the
actual point: this isn't a "no context" problem, it's a "the answer was never
written down as text" problem, and no amount of better chunking, better `k`,
or a better embedding model fixes it.

## The code, piece by piece

```python
store = build_vector_store()
retrieved = retrieve(QUESTION, store, k=2)
```

This is `naive_rag` Lesson 6's retrieval, verbatim: embed every note in
`fixtures/notes/`, embed the question, rank by cosine similarity, keep
the top `k`. `bike-repair.md` is in this course's fixtures precisely
because it's the note whose matching image
(`derailleur-hanger-diagram.png`) holds the answer, so watch what gets
retrieved for it.

```python
answer = generate_answer(QUESTION, retrieved)
```

Same generation step as `naive_rag` Lesson 7: stuff the retrieved chunks
into a prompt, ask Gemini to answer only from that context. `bike-repair.md`
will very likely be the top retrieved chunk, it's the most topically similar
note to a question about a derailleur hanger, but read its full text in
`fixtures/notes/bike-repair.md`: the torque spec is never mentioned, only "see
photo." Retrieval did its job correctly (it found the most relevant *text*),
and the answer is still wrong or an admission of not knowing, because the
fact it's being asked for isn't text at all.

## Running it

```bash
uv run python lessons/multimodal_rag/01_beginner/02_the_blind_spot_of_text_only_retrieval/lesson.py
```

## Expected output

```
Question: What's the torque spec for the rear derailleur hanger bolt, and what color is it printed in?

Retrieved (text-only): ['bike-repair.md', ...]

Answer from text-only RAG:
<an admission the context doesn't say, or a guess not backed by the retrieved text>

Retrieval worked correctly, it found the most relevant note. The note
itself just never wrote the answer down as text, only the image did.
```

## Checkpoint

- Text-only retrieval can fail even when it retrieves the *correct*
  document, if the answer inside that document lives in an image, not
  in the text.
- This is a different failure from Lesson 1's: that was "no context at
  all", this is "correct context, wrong modality."
- Fixing this needs a genuinely new capability (reading the image),
  not a better version of anything `naive_rag` already built. Lessons
  3-8 build exactly that capability, one piece at a time.

If anything here still feels unclear, ask before moving to Lesson 3.
