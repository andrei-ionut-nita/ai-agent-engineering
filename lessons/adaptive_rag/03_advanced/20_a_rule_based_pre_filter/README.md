# Lesson 20: A Rule-Based Pre-Filter

## Where we left off

Lesson 19 built three cheap signals and showed they're directional but
noisy, good enough to spot a clearly simple question, not precise enough
to tell "multi_hop" apart from "ambiguous" on their own. This lesson uses
that limitation on purpose: instead of replacing Lesson 3's LLM
classifier, use the cheap signals only to catch the confidently-simple
cases, and fall through to the real classifier for everything else.

## The code, piece by piece

```python
PRE_FILTER_THRESHOLD = 0.20
```

Chosen by inspecting Lesson 19's own five example scores directly (the
two clean `simple_factual` questions scored 0.135 and 0.120, everything
else scored 0.31 or higher), not from this course's Lesson 17 evaluation
set. That distinction matters and gets said explicitly here rather than
assumed: tuning a threshold against a different signal than the one you
later evaluate against is the safe pattern (see `naive_rag` Lesson 14's
threshold, chosen the same way), and Lesson 17 later in this course is
the deliberately-flagged case where that separation does NOT hold.

```python
def classify(query: str) -> tuple[str, bool]:
    score = complexity_score(query)
    if score < PRE_FILTER_THRESHOLD:
        return "simple_factual", False
    return classify_with_llm(query), True
```

Below the threshold, skip Gemini entirely and return `simple_factual`
directly. At or above it, fall through to the real LLM classifier from
Lesson 3, rebuilt here as `classify_with_llm()`. The pre-filter only ever
short-circuits to one label, on purpose: it isn't confident enough to
distinguish `multi_hop` from `ambiguous`, only "clearly simple" from
"needs the real classifier."

## Running it

```bash
uv run python lessons/adaptive_rag/03_advanced/20_a_rule_based_pre_filter/lesson.py
```

## Expected output

```
Q: What oven setting does the pizza dough recipe use?
   label=simple_factual  (via rule-based pre-filter)

Q: How often does the wind sensor need re-oiling?
   label=simple_factual  (via rule-based pre-filter)

Q: What two hobbies happen in the same room as the weather station?
   label=multi_hop  (via LLM classifier)

Q: How does wind speed affect things around the house?
   label=ambiguous  (via LLM classifier)

Gemini classification calls made: 2 / 4 questions
```

Half the questions here never touch the network. On a larger, more
skewed question set (most real traffic to a Q&A tool tends to be simple
lookups), that ratio would save considerably more.

## Checkpoint

- A rule-based pre-filter doesn't need to be as accurate as the model it
  sits in front of, it only needs to be confident enough on the cases it
  does handle, and honest enough to defer everything else.
- Threshold picked from a signal separate from Lesson 17's evaluation
  set, the safe tuning pattern this series' README calls out explicitly.
- This is a genuine cost optimization, not a routing-quality one: the
  pre-filtered questions get the exact same label the LLM classifier
  would have given them, just without paying for the call.

If anything here still feels unclear, ask before moving to Lesson 21.
