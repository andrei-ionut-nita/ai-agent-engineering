# Lesson 18: Intermediate Checkpoint - Notes Assistant That Reports Its Own Routing

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built entirely out of ideas from Lessons 10 through 17, combined
into one thing. If you can read `lesson.py` and understand why every
piece is there, you've mastered the Intermediate tier. If any piece
feels unfamiliar, that's a sign to revisit the lesson it came from
before continuing to Advanced.

## What it does

Loads (or builds and persists) an embedding index over every fixture
note, then answers three questions, one simple, one multi-hop, one
ambiguous, each routed automatically. Every answer discloses, in its own
text, which strategy handled it and why, and every routing decision is
logged to a local file for later inspection.

## Where each piece came from

```python
def classify_with_confidence(question: str) -> tuple[str, float]:
    ...
    return result["label"], float(result["confidence"])
```
Lesson 10: the classifier returns a label AND a confidence score, from
one structured-output call.

```python
def route(label: str, confidence: float, question: str, store: list[dict]) -> tuple[str, list[dict]]:
    if confidence < CONFIDENCE_THRESHOLD:
        return "multi_hop (fallback)", retrieve(question, store, k=2)
    ...
```
Lesson 11: below `CONFIDENCE_THRESHOLD` (read off Lesson 10's own
examples, not tuned against Lesson 17's evaluation set), the label is
set aside and retrieval falls back to the wider strategy.

```python
if label == "ambiguous":
    scored_all = retrieve(question, store, k=len(store))
    top1 = scored_all[:1]
    if grade_chunk(question, top1[0]["text"]) == "relevant":
        return "corrective", top1
    return "corrective", scored_all[:2]
```
Lesson 12's grading idea folded into the corrective route: grade the
top result before trusting it, widen only if the grade says no.

```python
def log_decision(entry: dict) -> None:
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(entry) + "\n")
```
Lesson 13: every routing decision, question, label, confidence,
strategy, sources, and call counts, appended to `routing_log.jsonl`.

```python
CALL_COUNTS = {"embed": 0, "generate": 0}
def reset_counts() -> None: ...
```
Lesson 14: call counts reset per question and logged alongside the
decision, so cost is visible per answer, not just aggregated.

```python
SYSTEM_PROMPT = """... End every answer with one final line in exactly this form:
Strategy used: <strategy name> (<one-line reason why this strategy fit this question>)"""
```
Lesson 15: the strategy and the reason for it are generated inside the
model's own answer text, not printed separately by this script.

(Lesson 16's misrouting failures and Lesson 17's evaluation don't
appear directly in this script's code, since this checkpoint routes
three clean, unambiguous demo questions rather than a labeled set
built to expose edge cases, but everything those lessons taught about
where routing can go wrong, and how honestly to measure whether it
helps, is what this script's design decisions rest on.)

## Running it

```bash
uv run python lessons/adaptive_rag/02_intermediate/18_intermediate_checkpoint_project/lesson.py
```

You should see: the pizza question answered by the naive route, the
same-room question answered by the multi-hop route, and the wind speed
question answered by the corrective route, each answer's final line
naming its own strategy and reason, followed by the matching entries in
`routing_log.jsonl`.

## Try this yourself

Without looking anything up:

- Delete `store.json` and rerun, confirm it re-embeds and rebuilds
  correctly.
- Lower `CONFIDENCE_THRESHOLD` to `0.5` and rerun, does the fallback
  route ever trigger anymore?
- Add a new fixture `.md` file, delete `store.json`, and ask a question
  only that new file can answer, does it get indexed, routed, and
  cited correctly on the next run?
- Open `routing_log.jsonl` after a few runs and check: which strategy
  got used most often, and does that match what you'd expect from the
  three demo questions?

If you can make these changes confidently, you're ready for the
Advanced tier, starting at Lesson 19.
