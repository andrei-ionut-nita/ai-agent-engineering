# Lesson 23: Building an agent from scratch

## What this reveals

The langchain course's `create_agent` (langchain course, lesson 23) felt
almost magical: hand it a model and some tools, and it handles an entire
loop of deciding whether to call a tool, running it, and asking again,
until it's ready to answer. It isn't magic. It's a small graph: a model
node, a tool-execution node, and one conditional edge connecting them in
a loop. This lesson builds that graph by hand, with the exact same
primitives you already know from Beginner Lesson 07, `StateGraph`,
`MessagesState`, `ToolNode`, `tools_condition`, just with a second tool
added so it feels like a real, general-purpose agent instead of a toy.

## Binding tools to the model

```python
model_with_tools = model.bind_tools(tools)
```

`bind_tools` attaches the tools' schemas (their names, descriptions, and
argument shapes) to every request sent to the model, so the model can
respond with a request to call one of them instead of plain text. This
single line is the part `create_agent` never shows you, it's doing this
exact call internally, once, when you pass it a `tools` list.

## The model node

```python
def call_model(state: MessagesState) -> dict:
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}
```

Same shape as every model node since Beginner Lesson 06: read the
accumulated messages, call the model, return the reply. The only
difference from a plain chatbot node is that this model was bound to
tools, so its reply might contain `tool_calls` instead of, or alongside,
plain text.

## Wiring the loop

```python
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
```

Three pieces make this a loop rather than a straight line:

- **`ToolNode(tools)`**: inspects the last message's `tool_calls`, runs
  the matching Python function(s), and wraps each result in a
  `ToolMessage` automatically. You never write "if the model asked for
  `calculator`, call `calculator`" yourself.
- **`tools_condition`**: a ready-made routing function. If the last
  message has pending tool calls, it routes to `"tools"`. Otherwise, it
  routes to `END`.
- **`builder.add_edge("tools", "agent")`**: after a tool runs, control
  goes straight back to the model, so it can either call another tool
  or, once it has enough information, answer in plain text.

That's the entire ReAct loop, four lines of graph wiring. Everything
`create_agent` does for you is contained in this shape.

## Running it

```bash
uv run python lessons/langgraph/03_advanced/23_building_an_agent_from_scratch/lesson.py
```

Ask it something that plausibly needs both tools in sequence, and the
printed trace shows the loop actually running more than once: a tool
call, a tool result, another tool call, another result, then a final
plain-text answer with no more tool calls pending.

## Checkpoint

- **`bind_tools`**: attaches tool schemas to every model request, the
  step `create_agent` performs invisibly.
- **`ToolNode`**: runs whichever tool(s) the model's last message
  requested, and packages the result as a `ToolMessage`.
- **`tools_condition`**: routes to `"tools"` if tool calls are pending,
  otherwise to `END`.
- **the loop**: `agent -> tools -> agent -> ... -> END`, a conditional
  edge plus one edge back, is the entire mechanism `create_agent`
  automates.

If anything here still feels unclear, ask before moving to Lesson 24.
