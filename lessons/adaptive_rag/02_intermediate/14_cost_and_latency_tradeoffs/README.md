# Lesson 14: Cost and Latency Tradeoffs

## Where we left off

Every earlier lesson asked "which strategy gets the right answer?" and
stopped there. This lesson asks the question routing actually exists to
answer: **at what cost?** Not every strategy that gets the right answer
costs the same to run, and routing that ignores cost entirely, always
reaching for the most powerful strategy just in case, throws away the
whole reason to route in the first place.

## What "cost" means here

This course makes no real-money API calls to measure, so cost here
means two things that are both real and both measurable directly:
**wall-clock time** (how long the strategy actually took) and **call
count** (how many embed and generate calls it made). Both track the
same underlying thing, more calls means more latency and more of
whatever the API actually charges per call, without needing to hardcode
a price that changes over time.

## The code, piece by piece

```python
def multi_hop_retrieve(question: str, store: list[dict]) -> list[dict]:
    first = retrieve(question, store, k=1)[0]
    followup_query = f"{question} (already found: {first['text'][:150]})"
    candidates = [r for r in retrieve(followup_query, store, k=2) if r["source"] != first["source"]]
    ...
```

Lessons 10-13's multi-hop stand-in was a single top-2 call, cheap but
not actually two hops. This lesson's version chains two real retrieval
steps, find the first document, then retrieve again using a follow-up
query built from what the first hop found, so its cost (two embed
calls instead of one) reflects what "multi-hop" actually implies:
retrieving more than once.

```python
def corrective_retrieve(question: str, store: list[dict]) -> list[dict]:
    scored_all = retrieve(question, store, k=len(store))
    top1 = scored_all[:1]
    grade = generate_text(grade_prompt).strip().lower()
    if "not_relevant" not in grade and "relevant" in grade:
        return top1
    return scored_all[:2]
```

Corrective's cost comes from a different place: not a second embed
call (the retry reuses scores already computed against every document,
`scored_all[:2]` instead of re-embedding), but a generate call to grade
the first result. Grading is what makes corrective retrieval
corrective; it's also the call that makes it more expensive than naive.

```python
def measure(strategy_name: str, question: str, store: list[dict]) -> dict:
    reset_counts()
    start = time.perf_counter()
    retrieved = STRATEGIES[strategy_name](question, store)
    elapsed = time.perf_counter() - start
    return {...}
```

`CALL_COUNTS`, incremented inside `embed_texts` and `generate_text`
themselves, is reset before each strategy runs, so the count reflects
exactly what that one strategy did, not calls left over from building
the vector store earlier.

## Running it

```bash
uv run python lessons/adaptive_rag/02_intermediate/14_cost_and_latency_tradeoffs/lesson.py
```

## Expected output

```
Q: What oven setting does the pizza dough recipe use?

     naive: 0.2xs, 1 embed call(s), 0 generate call(s), sources=['pizza-dough.md']
 multi_hop: 0.5xs, 2 embed call(s), 0 generate call(s), sources=['pizza-dough.md', ...]
corrective: 7.xxs, 1 embed call(s), 1 generate call(s), sources=['pizza-dough.md']
```

All three strategies retrieve `pizza-dough.md`, the correct source,
but corrective's grading call adds several seconds of latency for a
question that never needed grading in the first place, its top-1
result was correct all along. This is a genuinely cheap-and-sufficient
question: naive gets the same answer, fastest, for the fewest calls.

## Checkpoint

- **cost** in this course means wall-clock time and API call count,
  both measurable directly, without hardcoding a per-call price that
  changes over time.
- Multi-hop and corrective retrieval aren't free upgrades over naive,
  they cost real extra calls (a second hop, a grading call), and that
  cost is worth paying only when the question actually needs it.
- Routing to the cheapest *sufficient* strategy, not always the most
  powerful one, is the actual payoff of routing at all; if every
  question went down the most expensive path, there'd be no reason to
  classify anything first.

If anything here still feels unclear, ask before moving to Lesson 15.
