# Lesson 11: Query Planning and Decomposition

## Where we left off

Lesson 10 showed the *loop* handling multiple calls, but left the
*decision* to decompose entirely up to the model's unguided judgment.
That worked, but relying on it unprompted is fragile: some questions
get correctly split, others get a single broad query that quietly
misses one part. This lesson makes decomposition an explicit
instruction instead of an implicit hope.

## The code, piece by piece

```python
SYSTEM_INSTRUCTION = """You answer questions using a search_notes tool ...
If a question has more than one distinct part ... call search_notes
once per part, with a separate, focused query for each part ..."""

CONFIG = types.GenerateContentConfig(tools=[TOOLS], system_instruction=SYSTEM_INSTRUCTION)
```

`system_instruction` is a `GenerateContentConfig` field that sets
standing behavior for the whole conversation, separate from any single
user turn, the same conceptual role as a system prompt in other APIs.
Here it does one specific job: tell the model, explicitly, what
"decompose a compound question" means in terms of this tool
specifically (one focused query per part, don't combine early).

```python
sub_query = call.args["query"]
sub_queries.append(sub_query)
```

This lesson also collects every query the model actually searched for,
not just the final answer, so you can see the decomposition happen,
not just infer it happened from the answer being correct.

## Why an explicit instruction, not just a better tool description

Lesson 10's tool description already hinted at multi-document
retrieval ("call this again with a different query"), and often that
was enough. But a hint living inside one tool's description competes
for attention with everything else in the prompt, and doesn't
generalize if a second or third tool is added later. A `system_instruction`
states the *strategy* once, for the whole conversation, independent of
any one tool's wording, more robust, and the right place to add general
reasoning strategy instructions as this course's toolset grows.

## Running it

```bash
uv run python lessons/agentic_rag/02_intermediate/11_query_planning_and_decomposition/lesson.py
```

## Expected output

```
Compound question: What's the recommended cable-checking interval for the guitar pedalboard, and how far along is the Japanese study journal toward the JLPT N3 exam?

Sub-queries the model chose to search for, in order:
  1. 'guitar pedalboard cable checking interval'
  2. 'Japanese study journal JLPT N3 progress'

A: <a combined answer citing "every few months" for the cables and "roughly eighteen months in" for the JLPT N3 progress>
```

Exact query wording will vary between runs, the count (2 sub-queries,
one per part) is the reliable part to check.

## Checkpoint

- **`system_instruction`**: standing behavior for the whole
  conversation, the right place for a reasoning *strategy* ("decompose
  compound questions") rather than a single tool's usage note.
- Relying on the model to decompose a compound question with no
  explicit instruction works often enough to seem reliable and fails
  often enough to be a real risk on questions you haven't tested.
- **Try this yourself**: comment out `system_instruction=SYSTEM_INSTRUCTION`
  in `CONFIG` and rerun. Does the model still decompose the question
  into two searches, or does it search once with a broad query and miss
  one part? Either outcome is informative, this lesson's point is that
  you shouldn't have to guess which one happens.

If anything here still feels unclear, ask before moving to Lesson 12.
