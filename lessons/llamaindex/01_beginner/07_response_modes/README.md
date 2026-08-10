# Lesson 7: Response modes

## Naming what "synthesize" actually does

Lesson 5's `index.as_query_engine()` used a synthesis strategy without
naming it. This lesson names it: `response_mode` is the argument that
controls how a `QueryEngine` turns retrieved Nodes into one final
answer, the "synthesize" half of retrieve -> synthesize.

| `response_mode` | What it does | LLM calls |
|---|---|---|
| `"refine"` | Draft an answer from the first Node, then show each following Node plus the current draft and ask the LLM to refine it if the new Node adds anything | One per retrieved Node, sequential |
| `"compact"` (default) | Pack as much retrieved text as fits into one prompt, minimizing call count, then refine across however many batches that took | Usually 1 for small result sets |
| `"tree_summarize"` | Summarize Nodes in groups, then summarize those summaries, up to one final answer, a summarization tree | Scales with Node count, more parallelizable than `refine` |

`"compact"` is the default if you don't pass `response_mode` at all,
this is what Lesson 5 used implicitly. `"refine"` is the oldest, most
literal strategy, one careful pass per Node. `"tree_summarize"` is
built for large retrieved sets, dozens or more Nodes, where even
`"compact"`'s batching would still need many sequential refine calls;
building a tree instead lets more of that summarization work happen
in parallel.

## Why the outputs below look so similar

This course's fixture data is 3 Nodes total, and `similarity_top_k`
defaults to 2, so there's rarely more than 1-2 Nodes to synthesize from
in the first place. All three modes end up doing nearly the same
amount of work on nearly the same input, so don't expect night-and-day
differences below, and don't conclude from this lesson that the modes
don't matter. They matter a great deal once a query actually retrieves
a large `similarity_top_k` (Lesson 6) worth of Nodes, `refine`'s
sequential calls get slow, `compact` may need to split into several
prompts, and `tree_summarize` starts to clearly win on speed. The point
here is knowing the modes exist and what each one trades off, not
seeing a dramatic before/after.

## The code, piece by piece

```python
modes = ["refine", "compact", "tree_summarize"]
for mode in modes:
    query_engine = index.as_query_engine(response_mode=mode)
    response = query_engine.query(question)
```

Rebuilds a `QueryEngine` from the same index for each mode and asks it
the same question, so the only thing changing between iterations is
`response_mode`.

## Running it

```bash
uv run python lessons/llamaindex/01_beginner/07_response_modes/lesson.py
```

## Expected output

All wording below is LLM-synthesized and non-deterministic, your exact
phrasing and bullet grouping will vary between runs even for the same
mode. Captured from one real run:

```
Index built from 3 documents.

--- response_mode='refine' ---
Nimbus Robotics applies different rules for expense approval and reimbursement timing based on the amount and type of purchase:

* Expenses under 100 EUR: Can be submitted directly through the finance portal with a photo of a receipt and are typically reimbursed within 5 business days.
* Expenses over 100 EUR: Require pre-approval from a manager before spending the money, rather than after the fact.
...

--- response_mode='compact' ---
The rules for expense approval and reimbursement timing at Nimbus Robotics depend on the type and amount of the expense:

* Expenses under 100 EUR: Can be submitted directly through the finance portal with a photo of a receipt, and are typically reimbursed within 5 business days.
...
* Home office equipment: The one-time 800 EUR stipend is reimbursed against receipts submitted within the first 60 days of employment.
...

--- response_mode='tree_summarize' ---
Nimbus Robotics handles expense approvals and reimbursements according to the following guidelines:
...
* Home office equipment: A one-time 800 EUR stipend is provided for a desk, chair, and monitor, which is reimbursed against receipts submitted within the first 60 days of employment.
...
```

(Full answers for all three modes are printed when you actually run
it, trimmed here for length.) Worth noticing even on this tiny
dataset: `compact` and `tree_summarize` both mentioned the home office
equipment stipend (from `remote_work_policy.txt`, pulled in as the
retriever's second-closest match, same as Lesson 5's second query),
while `refine` didn't, a small, real example of how differently these
strategies can weigh secondary retrieved context even on identical
input.

## Checkpoint

- **`response_mode`**: the `as_query_engine()` argument controlling how
  retrieved Nodes get turned into one final answer.
- **`"compact"`** is the default: pack Nodes into as few prompts as
  possible, fewest LLM calls for small result sets.
- **`"refine"`**: one sequential LLM call per Node, each seeing the
  running draft, the most literal but most call-heavy strategy.
- **`"tree_summarize"`**: hierarchical summarization, built for large
  retrieved sets where the other two modes get slow or unwieldy.
- On tiny datasets like this course's, differences between modes are
  subtle. They become meaningful once `similarity_top_k` and dataset
  size grow.

If anything here still feels unclear, ask before moving to Lesson 8.
