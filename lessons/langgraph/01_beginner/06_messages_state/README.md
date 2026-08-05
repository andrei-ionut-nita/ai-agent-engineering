# Lesson 6: MessagesState, putting an AI model inside a node

## Where we left off

Every graph so far has been pure Python, no network calls, no AI. This
lesson finally puts a model call inside a node, and introduces the state
shape LangGraph provides specifically for conversations: `MessagesState`.

## Why messages need their own reducer

A conversation is a list that grows: system message, human message, AI
reply, maybe another human message, another AI reply, and so on. You
could model that with `Annotated[list, operator.add]` from Lesson 2,
and it would mostly work, but message lists have a wrinkle plain list
concatenation doesn't handle: sometimes you want to *replace* a specific
message already in the list (for example, a tool result correction),
not just always append. LangGraph ships a purpose-built reducer for this
called `add_messages`. It appends new messages onto the list like
`operator.add` would, but it also recognizes messages by their `id`, so
if a message with a matching `id` already exists in the list, it
updates that entry in place instead of duplicating it.

```python
from langgraph.graph import MessagesState
```

`MessagesState` is a ready-made `TypedDict` LangGraph provides with one
field, `messages`, already set up as
`Annotated[list, add_messages]`. You can write your own equivalent by
hand (and later lessons sometimes add fields alongside `messages` by
subclassing it), but for a graph that's "just a conversation," this
saves you from redefining the same thing every time.

## The code, piece by piece

```python
model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


def call_model(state: MessagesState) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}
```

This node reads the entire conversation so far (`state["messages"]`, a
list of `HumanMessage`, `AIMessage`, etc., the same message types from
the LangChain course) and calls `.invoke()` on the whole list, giving
the model full context. It returns `{"messages": [response]}`, a
single-item list containing just the new reply. Thanks to `add_messages`,
that single new message gets appended onto the existing conversation,
the node never needs to hand back the whole history it was just given.

```python
builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)
builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)
```

The graph shape itself is exactly Lesson 1's shape, one node, in and
out. What's new is entirely in the state definition and what the node
does with it.

```python
result = app.invoke({"messages": [HumanMessage("What is a graph, in one sentence?")]})
```

The initial state only needs to contain the first `HumanMessage`, the
model's reply gets appended by the node via `add_messages`. `result["messages"]`
after the run holds both: the original question and the new answer.

## Running it

```bash
uv run python lessons/langgraph/01_beginner/06_messages_state/lesson.py
```

## Checkpoint

- **`MessagesState`**: a ready-made state schema with one field,
  `messages`, using the `add_messages` reducer.
- **`add_messages`**: a reducer that appends new messages, but updates
  a message in place instead of duplicating it if the `id` matches one
  already in the list.
- **a node can call a model**: same `.invoke()` from the LangChain
  course, just called from inside a node function instead of directly
  in your script.
- **return only the new message(s)**: nodes hand back what changed,
  `[response]`, not the full growing conversation, the reducer handles
  appending it.

If anything here still feels unclear, ask before moving to Lesson 7.
