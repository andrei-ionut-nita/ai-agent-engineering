# Lesson 31: Multi-agent supervisor, an agent delegating to other agents

## The idea: an agent can BE a tool

Every tool since Lesson 13 has been a plain function. This lesson does
something that might feel strange at first: it wraps an **entire
agent**, with its own model, its own tools, its own internal tool-call
loop, as a single tool. From the outside, calling that tool looks
exactly like calling `calculator` or `word_counter`. What's running
underneath just happens to be far more sophisticated.

## Two independent specialists

```python
math_specialist = create_agent(
    model=model,
    tools=[calculator],
    system_prompt="You are a math specialist. Use the calculator tool for any arithmetic.",
)
text_specialist = create_agent(
    model=model,
    tools=[word_counter],
    system_prompt="You are a text-analysis specialist. Use the word_counter tool when relevant.",
)
```

Nothing new here at all, this is exactly `create_agent` from Lesson 23,
called twice, each with a narrower focus and only one tool. Each of
these could run entirely on its own, and in fact, they do, they have no
idea a supervisor exists.

## Wrapping an agent as a tool

```python
@tool
def ask_math_specialist(question: str) -> str:
    """Delegate a math or arithmetic question to the math specialist agent."""
    result = math_specialist.invoke({"messages": [HumanMessage(question)]})
    return result["messages"][-1].text
```

This is the key pattern of the whole lesson. `@tool` doesn't care what
happens inside the function it wraps, calling `calculator.invoke(...)`
directly, or calling an entire other agent's `.invoke(...)` and
returning its final answer, look identical from `@tool`'s perspective.
The docstring tells the *supervisor* when this tool is relevant, exactly
like every tool docstring since Lesson 13, it just happens to route to
a specialist agent instead of doing the calculation itself.

## The supervisor

```python
supervisor = create_agent(
    model=model,
    tools=[ask_math_specialist, ask_text_specialist],
    system_prompt=(
        "You are a supervisor. Delegate math questions to ask_math_specialist "
        "and text-analysis questions to ask_text_specialist. Don't answer "
        "those kinds of questions yourself."
    ),
)
```

The supervisor never sees `calculator` or `word_counter` directly, only
the two wrapped specialists. When you run the lesson and ask a math
question, the printed trace shows the supervisor delegating to
`ask_math_specialist`, which then, invisibly to the supervisor, runs
its own internal tool-call loop calling the real `calculator`. Two
layers of decision-making: which specialist to use, and then, within
that specialist, which of its own tools (if any) to use.

## Why bother with two layers, instead of one agent with four tools?

You could give one single agent all four tools (`calculator`,
`word_counter`, and whatever a math/text specialist might need) directly,
and for a project this small, that would work fine too.

The supervisor pattern earns its complexity as things grow: each
specialist can have its own carefully-tuned system prompt, its own
narrower set of tools (reducing the chance of the wrong tool getting
picked), and can be built, tested, and improved independently of the
others. A single "do-everything" agent's system prompt gets harder to
write correctly the more unrelated responsibilities you pile into it;
splitting responsibilities across specialists, coordinated by a
supervisor, keeps each piece focused and easier to reason about.

## Running it

```bash
uv run python lessons/langchain/03_advanced/31_multi_agent_supervisor/lesson.py
```

## Checkpoint

- **agent-as-tool**: wrapping an entire agent's `.invoke()` call inside
  a `@tool` function, so it can be handed to another agent exactly like
  any other tool.
- **supervisor**: an agent whose tools are themselves other agents,
  responsible for delegating, not doing the underlying work itself.
- **why split into specialists**: focused system prompts and narrower
  tool sets are each easier to get right than one agent handling
  everything.

If anything here still feels unclear, ask before moving to Lesson 32.
