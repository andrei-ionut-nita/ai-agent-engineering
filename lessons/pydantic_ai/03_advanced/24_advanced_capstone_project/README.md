# Lesson 24 (Capstone): An order-total assistant, end to end

## What you're building

A small "order assistant" agent that reads a plain-English order,
computes its total using an MCP-hosted calculator (not the model's own
arithmetic), and returns a validated `OrderResult`, wrapped in a
`FallbackModel` for resilience, and checked against a `pydantic_evals`
dataset. This pulls together the entire course:

- **`output_type`** (Lesson 3): the final answer is a validated
  `OrderResult`, not free text.
- **`deps_type` / `RunContext`** (Lesson 5, 7): the order's known
  catalog prices are injected as a dependency.
- **`MCPToolset`** (Lesson 21): arithmetic is delegated to a real MCP
  server (`server.py` in this folder), not left to the model to
  compute itself, the same "don't trust the model with arithmetic"
  lesson from the `langchain` course, now via MCP.
- **`FallbackModel`** (Lesson 22): a broken "primary" model falls back
  to the real one, same as Lesson 22, now wired into a realistic
  agent instead of a toy example.
- **`pydantic_evals`** (Lesson 15): a dataset checks that the computed
  total matches the expected total for a couple of sample orders.

## Why arithmetic goes through a tool, not the model

Language models are unreliable at multi-step arithmetic; this course's
`add`/`multiply` MCP tools guarantee a correct sum no matter how
complex the order gets, exactly like offloading arithmetic to a
calculator tool in the `langchain` course. Routing it through MCP
specifically (rather than a local `@agent.tool`) demonstrates that an
MCP server is a fully normal source of tools for a Pydantic AI agent,
not a special case.

## Running it

```bash
uv run python lessons/pydantic_ai/03_advanced/24_advanced_capstone_project/lesson.py
```

## What "done" looks like

- The agent prints a validated `OrderResult` for a sample order, with
  a total that matches manual arithmetic on the catalog prices.
- The `FallbackModel` printout shows the real model answered, even
  though the first model in the list was deliberately broken.
- The eval report at the end shows every case passing.

This is the last lesson in the course. If everything here makes sense,
you're ready to reach for Pydantic AI anywhere you'd have reached for
raw `langchain` before, when the shape of the agent's output matters as
much as what it says.
