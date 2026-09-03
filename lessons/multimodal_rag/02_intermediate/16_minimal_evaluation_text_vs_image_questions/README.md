# Lesson 16: Minimal Evaluation, Text vs. Image Questions

## Where we left off

`naive_rag` Lesson 17 introduced precision@k: a labeled set of
questions paired with known-correct sources, scored by whether the
correct source appears in the top `k` retrieved results. That metric
doesn't change here, precision@k doesn't care what a "source" is made
of. What's new is the **labeled set itself**: this course's set
deliberately mixes text-answerable and image-answerable questions, so
the score can be broken down by modality, not just reported as one
number, revealing whether retrieval is systematically weaker on one
modality than the other.

## The code, piece by piece

```python
LABELED_QUESTIONS = [
    ("How often does the chain and cassette get replaced?", "bike-repair.md"),
    ("What's the torque spec on the derailleur hanger bolt?", "derailleur-hanger-diagram.png"),
    ("What are the feed and discard fill lines on the starter jar?", "starter-jar-markings.png"),
    ("How fast does the terrarium's condensation clear in a working setup?", "terrarium.md"),
    ("What color are the RA and DEC motor cables?", "observatory-mount-wiring.png"),
]
```

Five questions, three expecting an image source, two expecting a text
source, deliberately unbalanced toward images since that's the modality
this course is actually testing (`naive_rag`'s equivalent set never had
to test anything but text).

```python
for (question, expected_source), query_vector in zip(LABELED_QUESTIONS, query_vectors):
    retrieved = retrieve_by_vector(query_vector, store, k)
    hit = expected_source in [r["source"] for r in retrieved]
    expected_modality = "image" if expected_source.endswith(".png") else "text"
    hits_by_modality[expected_modality].append(hit)
```

Same hit-counting logic as `naive_rag` Lesson 17, with one addition:
every hit (or miss) gets bucketed by the *expected* modality, so the
final score can be reported per modality (`precision@k for text
questions` vs. `precision@k for image questions`) as well as overall.

## Running it

```bash
uv run python lessons/multimodal_rag/02_intermediate/16_minimal_evaluation_text_vs_image_questions/lesson.py
```

## Expected output

```
precision@2:
  [HIT ] 'How often does the chain and cassette get replaced?' -> expected bike-repair.md, got [...]
  [HIT ] "What's the torque spec on the derailleur hanger bolt?" -> expected derailleur-hanger-diagram.png, got [...]
  ...
  Overall:      1.00 (5/5)
  Text-only:    1.00 (2/2)
  Image-only:   1.00 (3/3)
```

## Why this doesn't generalize (yet)

Five labeled questions has the exact same sample-size problem
`naive_rag` Lesson 17's "Why this doesn't generalize (yet)" section
covers in full: one flipped answer swings the overall score by 20
points, and it swings a per-modality score even further (one miss out
of two text questions is a 50-point swing). That section's two
warnings, that a small labeled set demonstrates the *mechanism* rather
than a trustworthy number, and that tuning a hyperparameter against the
same set you evaluate on invalidates the score, apply here without any
change, they're not re-derived in this lesson, go re-read that section
if it's not fresh.

## Checkpoint

- precision@k is unchanged from `naive_rag`; what's new is a labeled
  set spanning both modalities and a breakdown by modality, not just
  an overall number.
- A per-modality breakdown can reveal an asymmetry (retrieval reliably
  strong on text, weaker on images, or the reverse) that a single
  overall score would hide.
- Everything `naive_rag` Lesson 17 said about small-sample trust and
  tune/eval contamination applies here unchanged, see that lesson's
  "Why this doesn't generalize (yet)" section.

If anything here still feels unclear, ask before moving to Lesson 17.
