# Lesson 12: Multi-agent delegation

## An agent calling another agent

The `langgraph` course builds multi-agent systems as an explicit graph
of nodes. Pydantic AI's simplest multi-agent pattern is much more
direct: one agent's tool function just calls another agent, since
agents are plain Python objects with a `run_sync` method, nothing
special about calling one from inside a tool.

```python
joke_agent = Agent(
    "google:gemini-3.5-flash-lite",
    system_prompt="You write one short joke about the given topic.",
)

main_agent = Agent("google:gemini-3.5-flash-lite")

@main_agent.tool
def tell_joke(ctx: RunContext[None], topic: str) -> str:
    """Delegate to the joke-writing agent for a topic."""
    result = joke_agent.run_sync(topic, usage=ctx.usage)
    return result.output
```

From `main_agent`'s point of view, `tell_joke` is just another tool
with a string in, a string out. It has no idea the "tool" is secretly
a whole other LLM call. This is the cleanest way to give an agent a
specialist: a summarizer, a translator, a fact-checker, without
merging all that logic and prompting into one mega-agent.

## Why pass `usage=ctx.usage`

`ctx.usage` is the running usage total for the *outer* run. Passing it
into the delegated agent's `run_sync` means the sub-agent's token
usage accumulates into the same total, instead of being invisible to
whoever's tracking cost on the outer run. Lesson 13 covers usage
tracking and limits in depth; here, just note that passing `usage=`
through is what keeps delegated calls accounted for.

## When to reach for `langgraph` instead

This pattern is great for a handful of specialist calls with a clear
caller/callee relationship. Once you need cycles, shared mutable
state across many agents, or conditional branching between more than a
couple of participants, `langgraph`'s explicit graph model (or Lesson
17's `pydantic_graph`) becomes the better fit. Delegation-as-a-tool is
the "just call a function" option; a graph is the "model the control
flow explicitly" option.

## Running it

```bash
uv run python lessons/pydantic_ai/02_intermediate/12_multi_agent_delegation/lesson.py
```

## Checkpoint

- A tool function can call `another_agent.run_sync(...)` directly;
  agents are plain objects, nothing special is needed to nest them.
- Passing `usage=ctx.usage` into the nested call folds its token usage
  into the outer run's total.
- This pattern suits a few specialist delegations; genuinely complex
  control flow between agents belongs in a graph instead (Lesson 17).

If anything here still feels unclear, ask before moving to Lesson 13.
