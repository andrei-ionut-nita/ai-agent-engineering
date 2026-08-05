# Lesson 1: What is Pydantic AI?

## The problem it solves

In the `langchain` course, an agent's output is fundamentally a
string. If you wanted structured data back, you parsed the string
yourself, or reached for `with_structured_output` and hoped the model
cooperated. Pydantic AI starts from the opposite direction: you declare
the shape of the output you want as a Pydantic `BaseModel`, and the
framework guarantees you either get a validated instance of that model
back, or an error you can handle, never a string you have to hope is
JSON.

This isn't a competing "better LangChain." It's a narrower, more
opinionated framework built by the Pydantic team (the validation
library nearly every Python AI framework, including LangChain, already
depends on) specifically for the case where an agent's inputs and
outputs need to be *type-safe*: validated, IDE-autocompletable, and
caught by your type checker before they ever reach the model.

## The core idea: types in, types out

An `Agent` in Pydantic AI is generic over two things:

- **`deps_type`**: the type of runtime context/dependencies the agent
  and its tools can read (a database connection, a user ID, an API
  client). This is dependency injection, not a global.
- **`output_type`**: the type the agent's final answer must validate
  against. Default is `str`, but it can be any Pydantic model,
  dataclass, `TypedDict`, or `Union` of those.

Everything else in this course, tools, streaming, multi-agent
delegation, MCP, sits on top of that one idea: an agent is a function
from validated input to validated output, where the LLM fills in the
reasoning in between.

## How this maps onto LangChain concepts

| LangChain | Pydantic AI | Lesson |
|---|---|---|
| `@tool` / `bind_tools` | `@agent.tool` | 6, 7 |
| `with_structured_output` | `output_type=` | 3 |
| manual state passed through closures | `RunContext[Deps].deps` | 5 |
| LangGraph multi-agent graphs | agent-as-tool delegation | 12 |
| LangSmith datasets/evaluators | `pydantic_evals` | 15 |
| LangSmith tracing | OpenTelemetry / Logfire | 18 |
| `langchain-mcp-adapters` | `MCPToolset` | 21 |

## Running it

This lesson has no agent yet, just a script that prints the mental
model out so it's fixed in your head before Lesson 2 runs a real one.

```bash
uv run python lessons/pydantic_ai/01_beginner/01_what_is_pydantic_ai/lesson.py
```

## Expected output

No network calls here, just printed vocabulary, so this is exact:

```
Core idea:
  An Agent is generic over deps_type (what it can read at runtime) and output_type (what its final answer must validate against).

LangChain concept -> Pydantic AI equivalent:
  @tool / bind_tools               -> @agent.tool (Lessons 6-7)
  with_structured_output           -> output_type= (Lesson 3)
  closures for shared state        -> RunContext[Deps].deps (Lesson 5)
  LangGraph multi-agent graphs     -> agent-as-tool delegation (Lesson 12)
  LangSmith datasets/evaluators    -> pydantic_evals (Lesson 15)
  LangSmith tracing                -> OpenTelemetry / Logfire (Lesson 18)
  langchain-mcp-adapters           -> MCPToolset (Lesson 21)
```

If you see an error instead, check the
[Troubleshooting section](../../../../README.md#troubleshooting) in
this project's root README.

## Checkpoint

- Pydantic AI agents are generic over `deps_type` (what they can read)
  and `output_type` (what they must return).
- The default `output_type` is `str`; anything else is validated
  before you ever see it.
- Every concept in this course has a direct LangChain/LangGraph/
  LangSmith/MCP counterpart, just enforced by types instead of
  convention.

If anything here still feels unclear, ask before moving to Lesson 2,
where we run a real agent.
