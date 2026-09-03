# Lesson 15: Failure Modes of Captioning and Matching

## Where we left off

Every lesson so far assumed captioning works well enough. It doesn't
always, and this course's whole retrieval quality is bounded by caption
quality in a way `naive_rag` never had to worry about (there was no
lossy intermediate step between a document and its embedding). This
lesson shows two specific, real failures, on purpose, the same spirit
as `naive_rag` Lesson 16.

## Failure 1: a caption that drops a detail the image actually has

`CAPTION_PROMPT` (Lesson 4) asks for specificity, but a captioning
model can still summarize past a detail, especially a small or
secondary one. This lesson captions
`observatory-mount-wiring.png` with a deliberately *weaker* prompt (just
"describe this image"), and shows the resulting caption often omits the
"RA = red, DEC = blue" detail entirely, or states it vaguely ("colored
cables"), where Lesson 4's specific prompt reliably keeps it. Once a
detail is missing from a caption, it's gone for retrieval, no amount of
clever ranking recovers a fact the caption never wrote down; the image
itself would still have the answer, but nothing points a search at it
anymore.

## Failure 2: a caption matches a query, but the image doesn't answer it

The reverse failure: a caption can be semantically similar to a query
without the underlying image actually containing what's asked.
`starter-jar-markings.png`'s caption mentions "jar" and "levels";
a query about "what jar size is used for the starter" scores that
caption fairly high on similarity (both are about the jar), but the
image never actually shows the jar's volume, only the two fill lines.
Retrieval returns a plausible-looking match; generation, looking at the
actual image, correctly has to admit it doesn't show that.

## The code, piece by piece

```python
WEAK_CAPTION_PROMPT = "Describe this image."
strong_caption = caption_image(IMAGE_PATH, CAPTION_PROMPT)
weak_caption = caption_image(IMAGE_PATH, WEAK_CAPTION_PROMPT)
```

Same function, same image, only the prompt's specificity changes,
isolating exactly one variable so the difference in what survives into
each caption is attributable to the prompt, not to randomness in the
model's output between two separate images.

## Running it

```bash
uv run python lessons/multimodal_rag/02_intermediate/15_failure_modes_of_captioning_and_matching/lesson.py
```

## Expected output

```
--- Failure 1: a caption that drops a detail ---

Strong prompt caption:
<mentions "RA = red" and "DEC = blue" explicitly>

Weak prompt caption:
<may omit or vaguely describe the cable colors>

--- Failure 2: caption matches, image doesn't answer ---

Query: 'What jar size (volume) is used for the starter?'
Retrieved: starter-jar-markings.png (score=0.XX)
Answer: <an honest admission the image shows fill lines, not the jar's total volume>
```

## Checkpoint

- Caption quality bounds retrieval quality; a vague caption makes a
  real detail permanently unretrievable, even though the image itself
  still has it.
- A caption matching a query semantically doesn't guarantee the
  underlying image actually answers the question, generation re-reading
  the original image (Lesson 8) is what catches this, by admitting it
  honestly instead of hallucinating an answer.
- Both failures are reasons to keep `CAPTION_PROMPT` specific (Lesson
  4) and to keep re-attaching the original image at generation time
  (Lesson 8) rather than trusting the caption as the final answer.

If anything here still feels unclear, ask before moving to Lesson 16.
