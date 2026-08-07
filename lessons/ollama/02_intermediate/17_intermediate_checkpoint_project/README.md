# Lesson 17 (Checkpoint): Tool-Calling Local Agent

## What this combines

Nothing new here, this is where the intermediate tier's pieces meet:

- **Tool calling** (Lesson 11): two real tools, `get_weather` and
  `calculate`, described with the same JSON Schema shape as structured
  output.
- **Multi-turn memory** (Lesson 12): one growing `messages` list reused
  across three separate questions, not rebuilt each time.
- **The full agent loop**: not just one ask/call/respond round trip,
  but looped until the model stops asking for tools at all.

And, running through everything, the theme of this whole course: no
`.env`, no API key, no internet, the entire agent runs against
`llama3.2` on your own machine.

## Why the loop, not a single round trip

Lesson 11 called a tool exactly once, then made one more call to get a
final answer. That's fine for a simple case, but a real question might
need several tools in sequence, or even the same tool called more than
once, before the model has everything it needs.

```python
def run_agent(messages: list[dict]) -> str:
    while True:
        response = ollama.chat(model="llama3.2", messages=messages, tools=TOOLS)
        messages.append(response.message)

        if not response.message.tool_calls:
            return response.message.content

        for call in response.message.tool_calls:
            function = FUNCTIONS[call.function.name]
            result = function(**call.function.arguments)
            messages.append({"role": "tool", "content": result, "tool_name": call.function.name})
```

This keeps calling the model and appending results until a response
comes back with an empty `tool_calls`, meaning the model judged it had
enough information to answer in plain language. `FUNCTIONS` maps a
tool's name (a string, exactly as the model requests it) to the real
Python function that does the work, so `run_agent` never needs an
`if/elif` chain to dispatch calls, just a dictionary lookup.

## The third question is the real test

```python
messages.append({"role": "user", "content": "What is the weather in Tokyo?"})
run_agent(messages)   # Q1

messages.append({"role": "user", "content": "What is 47 * 12?"})
run_agent(messages)   # Q2

messages.append({"role": "user", "content": "Was the city I asked about earlier warmer or colder than 20 degrees?"})
run_agent(messages)   # Q3
```

Question 3 doesn't name Tokyo at all, it can only be answered
correctly if the model still has Q1's tool result sitting in its
conversation history AND is willing to reason about that number
against "20 degrees" without calling any new tool. If this answers
correctly, both this tier's core ideas, tool calling and real memory,
are demonstrably working together, not just individually.

## Running it

```bash
uv run python lessons/ollama/02_intermediate/17_intermediate_checkpoint_project/lesson.py
```

## Expected output

```
Q1: What is the weather in Tokyo?
A1: The current weather in Tokyo is 25 degrees Celsius, with plenty of sunshine.

Q2: What is 47 * 12?
A2: The result of 47 multiplied by 12 is 564.

Q3: Was the city I asked about earlier warmer or colder than 20 degrees?
A3: Tokyo's current weather is 25 degrees Celsius, which is warmer than 20 degrees Celsius.
```

Exact wording will vary, but A2 should always say 564 (a real
calculation, not a guess), and A3 should always correctly identify
Tokyo and correctly say "warmer."

## Checkpoint

If this lesson ran cleanly and made sense without looking anything up,
you're ready for the advanced tier. You should be able to explain, in
your own words:

- Why the agent loop is a `while True`, not a fixed number of calls
  (Lesson 11, extended).
- How `FUNCTIONS[call.function.name]` avoids an `if/elif` dispatch
  chain.
- Why Q3 requires both tool calling AND multi-turn memory to answer
  correctly (Lessons 11 and 12, together).
- What `NativeOutput` bought you over pydantic_ai's default structured
  output, and why it mattered specifically for a local model (Lesson 14).

If any of those feel shaky, it's worth a quick re-read of that lesson
before continuing into the advanced tier, where hardware, context
limits, and production concerns take over.
