# Lesson 12: Agentic Tool-Based Routing

## Where we left off

Every routing lesson so far has had the same two-step shape: call the
model to classify the question into a label (Beginner Lessons 3, 10),
then this course's own code looks that label up in a routing table to
decide which strategy to run (Beginner Lesson 4). This lesson collapses
that into one step: instead of asking "what label is this question,"
hand the model the three strategies directly, as tools, and let it pick
one.

## A tool per strategy, not a tool per document

`agentic_rag` Lesson 3 declared one tool, `get_current_temperature`, and
let the model decide whether to call it. This lesson does the same
thing with three tools, one per retrieval strategy, and no arguments at
all, calling a tool by name already communicates the whole decision:

```python
USE_NAIVE_DECLARATION = types.FunctionDeclaration(
    name="use_naive_retrieval",
    description=(
        "Use for a specific factual lookup answerable from a single "
        "passage in ONE document (a number, a setting, a schedule)."
    ),
)
```

The three tools' `description` fields carry the same routing logic
Beginner Lesson 3's classify prompt used to hold, simple-factual,
multi-hop, or ambiguous, just phrased as instructions for when to call
each tool instead of instructions for how to label a question.

## The code, piece by piece

```python
response = client.models.generate_content(
    model=CHAT_MODEL,
    contents=prompt,
    config=types.GenerateContentConfig(tools=[ROUTING_TOOL], temperature=0),
)
calls = response.function_calls
tool_name = calls[0].name if calls else "use_naive_retrieval"
retrieved = STRATEGIES[tool_name](question, store)
```

One call, not two: no separate classify step, no routing table lookup
afterward. `response.function_calls` is the model's chosen tool, and
`STRATEGIES` (a plain dict of name to function, the same registry idea
`agentic_rag` Lesson 21 built) is what actually runs it. Nothing was
executed by Gemini itself, exactly like `agentic_rag` Lesson 3, the
model only requested a named call; this course's own code decides to
honor it.

## Running it

```bash
uv run python lessons/adaptive_rag/02_intermediate/12_agentic_tool_based_routing/lesson.py
```

## Expected output

```
Q: What oven setting does the pizza dough recipe use?
  tool chosen: use_naive_retrieval
  sources retrieved: ['pizza-dough.md']

Q: What two hobbies happen in the same room as the weather station?
  tool chosen: use_multi_hop_retrieval
  sources retrieved: ['bookshelf.md', 'weather-station.md']

Q: How does wind speed affect things around the house?
  tool chosen: use_corrective_retrieval
  sources retrieved: ['garden.md']
```

The exact chunks retrieved for the multi-hop question can vary run to
run (top-2 similarity search sometimes prefers `weather-station.md`
over `cello-practice.md`, both mention the same room), but the tool
choice itself is stable: a clean single-document lookup picks
`use_naive_retrieval`, a question that names two related activities
picks `use_multi_hop_retrieval`, and the vague, cross-cutting wind
speed question picks `use_corrective_retrieval`.

## Comparing to the separate-classifier approach

Beginner Lessons 3-9 (a classifier call, then a routing table lookup)
and this lesson (one tool-call decision) both end up choosing between
the same three strategies, but where that decision lives is different:

- **Separate classifier**: the routing logic lives in your own
  readable `if/elif` code, easy to test, log, and override by hand,
  with one guaranteed extra API call before retrieval ever starts.
- **Tool-based routing**: the routing logic lives inside the model's
  judgment call, harder to inspect (there's no label to print and
  reason about separately from the retrieval that follows), but it's
  one call instead of two, and there's no separate routing table that
  can drift out of sync with the strategies it's supposed to point to.

Neither is strictly better, they're the same decision made in two
different places, with different tradeoffs for cost and inspectability.

## Checkpoint

- **tool-based routing**: handing the model the retrieval strategies
  themselves as callable tools, so choosing one *is* the routing
  decision, no separate label step.
- A tool's `description` field carries the routing logic that used to
  live in a classify prompt, phrased as "when to call this" instead of
  "what to label this."
- Fewer calls, less inspectability: the same tradeoff every "let the
  model decide" choice makes against "decide it yourself, explicitly,
  in code."

If anything here still feels unclear, ask before moving to Lesson 13.
