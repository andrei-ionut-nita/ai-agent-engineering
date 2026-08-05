# Lesson 23: create_agent, automating the tool-call loop

## What changes here

In Lesson 14, we wrote the tool-call loop ourselves: ask the model, check
`ai_message.tool_calls`, run the tool, send a `ToolMessage` back, ask
again. That was worth doing by hand once, it's how you actually learn
what's happening instead of trusting a framework blindly. But doing it
by hand every time you build something would be tedious, especially once
a task needs several tool calls in a row, or several different tools.

`create_agent`, from LangGraph (the lower-level engine LangChain's agents
are built on), automates that loop. This is the first lesson where we're
building something that actually deserves to be called an **agent**:
something that can decide, on its own, to take multiple actions in order
to answer you, not just respond in one shot.

## Building the agent

```python
agent = create_agent(
    model=model,
    tools=[calculator],
    system_prompt="You are a helpful assistant with access to a calculator tool.",
)
```

Three pieces, all familiar:

- **`model`**: the same `ChatGoogleGenerativeAI` object from every
  earlier lesson.
- **`tools`**: a list of `@tool`-decorated functions, same calculator
  from Lesson 13. You could list more than one; Lesson 15 covers that.
- **`system_prompt`**: standing instructions, same idea as the
  `"system"` message in Lesson 3's template.

`create_agent` returns something you still call `.invoke()` on, but this
time it's not calling the model directly, it's running an entire loop
internally: check if a tool is needed, run it if so, check again, repeat,
until the model is ready to give a final answer with no more tool calls
pending. The three manual rounds from Lesson 14 now happen inside one
`.invoke()` call, and it would automatically run more rounds than three
if a harder question needed them.

## No memory here, on purpose

```python
result = agent.invoke({"messages": [HumanMessage("What is 293 times 481?")]})
...
result2 = agent.invoke({"messages": [HumanMessage("What numbers did I just ask you to multiply?")]})
```

Notice the second call has no idea the first one happened, the agent
correctly says it hasn't been asked to multiply anything yet. This is
deliberate: this lesson isolates "automating the tool loop" as its own
concept, before Lesson 24 adds memory on top. Each `.invoke()` here is
still as independent as every plain `model.invoke()` call has been since
Lesson 1.

## Reading the result

```python
result["messages"][-1].text
```

`create_agent`'s result is a dictionary with a `"messages"` key holding
the entire conversation as the agent understands it for that one call,
including any tool calls and tool results that happened along the way,
same shape as the `messages` list you built by hand in Lesson 14. The
last entry is always the agent's actual final reply.

## Running it

```bash
uv run python lessons/langchain/03_advanced/23_create_agent_basics/lesson.py
```

You should see an exact multiplication answer (the calculator did the
math), followed by a second answer showing the agent has no idea what
was asked moments ago.

## Checkpoint

- **agent**: something that can decide, on its own, to take multiple
  steps (like calling tools) across more than one round, before giving a
  final answer.
- **`create_agent`**: builds a ready-to-use agent from a model, a list of
  tools, and a system prompt, automating the loop from Lesson 14.
- **still no memory**: without a checkpointer, each `.invoke()` call
  remains completely independent, just like a plain model.

If anything here still feels unclear, ask before moving to Lesson 24,
where we give this agent real memory.
