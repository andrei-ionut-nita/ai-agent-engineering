# Lesson 19: Where Per-Query Image Re-Captioning Gets Expensive

## Where we left off

This course's design (Lesson 1) caches one thing and re-pays for
another: captioning happens once per image, at store-build time
(cached via Lesson 12's persistence), but Lesson 8's generation step
re-reads the *original image* every time it's retrieved, a fresh vision
call, every query, for every image that shows up in that query's top
`k`. This lesson makes that cost visible instead of letting it stay
implicit.

## Why re-attaching the image at generation time isn't free

A vision call (an image `Part` in `contents`) costs more, in both
latency and tokens billed, than a text-only call of similar length,
Gemini has to process the actual pixels, not just a short string. Lesson
8 chose to pay this cost anyway, on purpose, because a caption alone can
miss a detail a specific question needs (Lesson 15's Failure 1). That
tradeoff was correct for this course's tiny fixture set, four images
total. It stops being obviously correct once a corpus has thousands of
images and a production query volume: re-reading a retrieved image on
every single query multiplies the vision-call cost by however many
times that image gets retrieved, where captioning only ever paid it
once.

## The code, piece by piece

```python
def time_caption_only(image_path: Path) -> float:
    start = time.perf_counter()
    caption_image(image_path)
    return time.perf_counter() - start


def time_generation_with_image(image_path: Path, query: str) -> float:
    start = time.perf_counter()
    generate_answer_with_image(image_path, query)
    return time.perf_counter() - start
```

Two timed calls against the same image: one captioning call (paid once,
ever, per image), one generation call that re-attaches the original
image (paid on every retrieval). Timing them side by side, then
projecting `generation_time * expected_retrievals_per_image` against
`caption_time * 1`, makes the asymmetry concrete instead of abstract.

## Running it

```bash
uv run python lessons/multimodal_rag/03_advanced/19_where_per_query_captioning_gets_expensive/lesson.py
```

## Expected output

```
Captioning (paid once): 1.8234s
Generation with re-attached image (paid per retrieval): 2.1032s

If this image is retrieved 100 times/day:
  Captioning cost (one-time):      1.8234s total
  Re-attachment cost (cumulative): 210.3200s/day
```

## Checkpoint

- Captioning is a one-time cost per image; re-attaching the original
  image at generation time is a recurring cost, paid on every
  retrieval.
- This course's choice (re-attach on retrieval, Lesson 8) trades
  ongoing cost for accuracy on cases a caption alone would miss
  (Lesson 15); at scale, that tradeoff needs revisiting, not assuming.
- One option not built in this course: caching the *generation* answer
  itself per (image, question-type) pair, not just the caption, out of
  scope here but worth knowing exists.

If anything here still feels unclear, ask before moving to Lesson 20.
