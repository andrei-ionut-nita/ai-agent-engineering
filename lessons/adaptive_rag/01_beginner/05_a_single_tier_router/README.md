# Lesson 5: A Single-Tier Router

## Where we left off

Lesson 4 built two routes and dispatched between them with an `if`
chain. That works at two routes. This lesson doesn't add a new
strategy, it cleans the exact same two routes up into the shape this
course keeps reusing for the rest of the Beginner tier: one
`classify()`, one `route()`, one dict mapping labels to strategy
functions, and one `answer()` that ties classify and route together
into the single entry point everything else calls.

## The shape, not new mechanics

```python
STRATEGIES: dict[str, Callable[[str, list[dict]], str]] = {
    "simple_factual": answer_simple,
    "multi_hop": answer_multi_hop,
}


def route(question: str, label: str, store: list[dict]) -> str:
    strategy = STRATEGIES.get(label)
    if strategy is None:
        raise ValueError(f"No route for label {label!r} yet, that's Lesson 6")
    return strategy(question, store)
```

A dict lookup instead of a chain of `if`/`elif` isn't a meaningfully
different amount of code at two entries, the payoff shows up in Lesson
6: adding the `ambiguous` route means adding one line to `STRATEGIES`,
not editing a growing conditional. This is the same registry idea
`agentic_rag` uses for tool dispatch and this course's own Lesson 22
formalizes further, introduced here at the smallest possible scale.

```python
def answer(question: str, store: list[dict]) -> tuple[str, str]:
    classification = classify(question)
    result = route(question, classification.label, store)
    return classification.label, result
```

This is the function every later lesson in this tier calls. Classify
first, route second, nothing else happens in between. Everything this
course adds from here, the third route in Lesson 6, the evaluation in
Lesson 7, the end-to-end script in Lesson 8, calls `answer()` or a
close variant of it, not `classify()` and `route()` separately.

## A rate-limit detail worth noticing

This lesson also introduces `call_model()`, a thin wrapper around
`generate_content` that retries once with a short backoff on a 429
(rate limited) response. The free tier allows 15 requests per minute
for this chat model, and a lesson that classifies and then generates for
several questions in a row can bump into that limit. This isn't a new
RAG concept, it's the same backoff-and-retry pattern `corrective_rag`
introduced in its own Lesson 6, reused here because this course now
makes enough calls per run to need it too.

## Running it

```bash
uv run python lessons/adaptive_rag/01_beginner/05_a_single_tier_router/lesson.py
```

## Expected output

```
Q: What oven setting does the pizza dough recipe use?
  label: simple_factual
  A: <the highest oven setting, with a preheated steel>

Q: How often does the wind sensor need re-oiling?
  label: simple_factual
  A: <every few months>

Q: What two hobbies happen in the same room as the weather station?
  label: multi_hop
  A: <should reference both cello practice and the bookshelf, in the study>
```

Gemini's exact wording, and occasionally its confidence in stating both
hobbies plainly versus hedging, varies run to run; what should stay
consistent is the label for each question and that the multi-hop
answer's context includes both `bookshelf.md` and `cello-practice.md`
material, not just one.

## Checkpoint

- **the reusable shape**: one classifier, one label-to-strategy dict,
  one `route()` that looks the label up, one `answer()` that chains
  classify and route together, this is the pattern every later lesson
  in this tier extends rather than replaces.
- A dict-based dispatch scales to a new route by adding one entry, not
  by editing a growing conditional.
- `call_model()`'s retry-on-429 wrapper isn't a RAG concept, it's
  operational plumbing this course needs once it's making several calls
  per run.

If anything here still feels unclear, ask before moving to Lesson 6.
