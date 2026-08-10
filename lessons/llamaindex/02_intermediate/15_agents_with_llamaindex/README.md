# Lesson 15: Agents with LlamaIndex, FunctionAgent

## From one decision to a loop

Lesson 14's `predict_and_call()` made exactly one tool-calling decision and
stopped. A real agent needs to do that repeatedly: call a tool, look at
the result, decide whether that's enough to answer or whether another tool
call is needed, and keep going until it has what it needs. `FunctionAgent`
is LlamaIndex's standard implementation of that loop, built on the
`llama-index-workflows` engine (also installed in this project), which
also backs `ReActAgent`, `AgentWorkflow`, and `CodeActAgent` for more
specialized cases this course doesn't cover.

| | LangChain | LlamaIndex |
|---|---|---|
| Standard single-agent class | `create_agent(model, tools=...)` | `FunctionAgent(tools=..., llm=..., system_prompt=...)` |
| Underlying mechanism | LangGraph loop | `llama-index-workflows` loop |
| Runs tool calls | Automatically, until a final answer | Automatically, until a final answer |
| Invocation | `agent.invoke({"messages": [...]})` | `await agent.run(user_msg=...)` (async) |

## `FunctionAgent` is async

Every workflow-based agent in LlamaIndex is asynchronous. `agent.run(...)`
returns a `WorkflowHandler`, itself awaitable, and actually executing the
loop requires `await`-ing it. A synchronous script therefore needs
`asyncio.run(...)` around an async entry point, this lesson's `main()` is
a thin sync wrapper around an async `run_agent()` for exactly that reason.

## The code, piece by piece

```python
agent = FunctionAgent(
    tools=[
        FunctionTool.from_defaults(fn=get_expense_limit),
        FunctionTool.from_defaults(fn=convert_eur_to_usd),
    ],
    llm=Settings.llm,
    system_prompt=(
        "You are a Nimbus Robotics expense assistant. Use the "
        "get_expense_limit tool to look up reimbursement limits, and "
        "convert_eur_to_usd when a question needs a USD figure. Keep "
        "answers short."
    ),
)
```

Two `FunctionTool`s, built exactly the way Lesson 14 built one (`get_expense_limit`
is reused unchanged), plus a second trivial tool, a fixed-rate EUR-to-USD
conversion. `system_prompt` steers the agent's judgment about which tool
to reach for and when, the same role a system message plays for any
LangChain agent.

```python
response = await agent.run(user_msg=question)
```

Runs the agent loop on one question. Internally, `FunctionAgent` calls its
`take_step()` method repeatedly: send the conversation (plus any tool
results so far) to the LLM, check whether it asked for a tool call, run
the tool if so and feed the result back in, and repeat until the LLM
responds with no further tool calls, at which point that response is the
final answer. The question this lesson asks needs both tools in sequence
(look up the EUR limit, then convert it), so the agent's internal loop
runs at least two rounds before answering.

```python
print(f"\nFinal answer:\n  {response}")
```

The awaited result is an `AgentOutput`. `str()` on it returns the final
message's text (`response.response.content`), which is what gets printed.

## Running it

```bash
uv run python lessons/llamaindex/02_intermediate/15_agents_with_llamaindex/lesson.py
```

## Expected output

Captured from a real run. The exact tool-call ordering, intermediate
reasoning, and final phrasing can vary between runs, this is one real
example:

```
Question: What is the hotel expense limit, and what is that limit in USD?

Final answer:
  The hotel reimbursement limit is 150 EUR per night, which is approximately 162.00 USD.
```

## Checkpoint

- **`FunctionAgent`**: LlamaIndex's standard tool-calling agent, built on
  `llama-index-workflows`, the loop version of Lesson 14's single
  `predict_and_call()` decision.
- Construct it with `tools=[...]`, `llm=...`, and `system_prompt=...`,
  the same shape of inputs as any agent framework.
- It's async: `await agent.run(user_msg=...)` inside an `asyncio.run(...)`-wrapped
  entry point, not a plain synchronous call.
- The returned `AgentOutput`'s `str()` is the final answer text, after
  however many internal tool-call rounds it took to get there.

If anything here still feels unclear, ask before moving to Lesson 16.
