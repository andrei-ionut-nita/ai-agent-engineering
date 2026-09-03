# Lesson 14: Prompting for Modality-Cited Answers

## Where we left off

`naive_rag` Lesson 15 taught grounded answers that cite a source file:
"(according to garden.md)". That's not quite enough information once a
citation might point at an image instead of a document, "according to
bike-repair.md" is misleading if the actual fact came from
`derailleur-hanger-diagram.png`, a different file entirely, attached
because it's the image that document references. This lesson extends
the citation instruction to name **which modality** a fact came from,
not just which file.

## The code, piece by piece

```python
def build_context_label(record: dict) -> str:
    if record["modality"] == "image":
        return f"an image ({record['source']})"
    return f"a text note ({record['source']})"
```

One small function that turns a record into a citation-ready label,
`"an image (derailleur-hanger-diagram.png)"` or `"a text note
(bike-repair.md)"`. This label, not the raw filename, goes into the
prompt's context section, so the model has the modality distinction
available to cite directly.

```python
prompt = f"""Answer the question using only the context below.

Rules:
- Every claim must cite its source, including whether it came from a text note or an image, like this: (according to the image derailleur-hanger-diagram.png).
- If the context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {query}"""
```

`naive_rag` Lesson 15's exact rule structure, one clause added:
"including whether it came from a text note or an image." Nothing else
about the grounding rules changes, honest citation and admitting
ignorance are exactly as important here as they were for text-only RAG,
this just extends what "citation" means once a source can be a picture.

## Running it

```bash
uv run python lessons/multimodal_rag/02_intermediate/14_prompting_for_modality_cited_answers/lesson.py
```

## Expected output

```
Q: What's the torque spec for the derailleur hanger bolt?
A: The torque spec is 8 Nm, printed in red (according to the image derailleur-hanger-diagram.png).

Q: How often does the chain and cassette get replaced?
A: Roughly every 3,000 km (according to the text note bike-repair.md).
```

## Checkpoint

- Citing "which file" isn't enough once a fact can come from an image
  attached to a *different* file than the one the question seems to be
  about; citing "which modality, and which file" is unambiguous.
- The prompt change is one clause, not a new grounding philosophy,
  `naive_rag` Lesson 15's honesty rules (cite everything, admit
  ignorance) still apply exactly as written.

If anything here still feels unclear, ask before moving to Lesson 15.
