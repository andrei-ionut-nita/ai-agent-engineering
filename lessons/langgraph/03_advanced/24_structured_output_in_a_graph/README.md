# Lesson 24: Structured output inside a graph node

## Why this belongs in a node

`with_structured_output` (langchain course, lesson 18) already showed
that a model can return a validated Pydantic object instead of loose
text. Nothing about that changes inside a graph, the interesting part is
what happens next: a downstream node can read specific fields out of
that object and make a decision, exactly like Beginner Lesson 4's
conditional routing, except now the thing being routed on was extracted
by the model itself, not typed in by hand.

## The schema

```python
class FeedbackAnalysis(BaseModel):
    topic: str = Field(description="The single main subject of the feedback, in a few words.")
    sentiment: Literal["positive", "negative", "neutral"] = Field(
        description="The overall sentiment of the feedback."
    )
```

Same idea as any Pydantic model since the langchain course, a shape the
model has to fill in correctly. `Literal[...]` constrains `sentiment` to
exactly three allowed values, so the downstream node can safely assume
it never sees anything else.

## The extraction node

```python
structured_model = model.with_structured_output(FeedbackAnalysis)

def extract(state: State) -> dict:
    last_user_message = state["messages"][-1].content
    analysis = structured_model.invoke(last_user_message)
    return {"topic": analysis.topic, "sentiment": analysis.sentiment}
```

`structured_model.invoke(...)` returns a `FeedbackAnalysis` instance
directly, not an `AIMessage`, there's no `.tool_calls` or `.text` to
unwrap here. The node pulls `topic` and `sentiment` off that object and
writes them into two new state fields.

## The state fields with no reducer

```python
class State(TypedDict):
    messages: list
    topic: str
    sentiment: str
```

`topic` and `sentiment` are plain `str` fields, no `Annotated` reducer
like `add_messages`. That means whichever node writes to them simply
replaces the previous value, appropriate here since each run should hold
exactly one topic and one sentiment, not a growing list of them.

## Routing on what the model extracted

```python
def respond(state: State) -> dict:
    if state["sentiment"] == "negative":
        reply = f"I'm sorry to hear about the trouble with {state['topic']}. ..."
    elif state["sentiment"] == "positive":
        reply = f"Glad to hear {state['topic']} is working well for you!"
    else:
        reply = f"Thanks for the note about {state['topic']}."
    return {"messages": [reply]}
```

`respond` never looks at the raw feedback text again. It trusts the
structured fields `extract` already wrote, the same separation of
concerns as any two-node pipeline: one node's job is to understand, the
next node's job is to act on that understanding.

## Running it

```bash
uv run python lessons/langgraph/03_advanced/24_structured_output_in_a_graph/lesson.py
```

You'll see the extracted `topic`/`sentiment` printed for each piece of
feedback, followed by a reply shaped entirely by those two fields.

## Checkpoint

- **structured output in a node**: `with_structured_output` works
  identically inside a node as it does at the top level, it just writes
  into state instead of standing alone.
- **no reducer on a field**: plain `str` (or any type without
  `Annotated[..., reducer]`) means "replace", not "accumulate".
- **routing on extracted fields**: a downstream node can make decisions
  based on structured data an earlier node derived from free text.

If anything here still feels unclear, ask before moving to Lesson 25.
